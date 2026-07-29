import logging
import os
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from pydantic_ai import Agent, UsageLimits
from rustprint.src.agent_retry import run_agent_with_retry
from dataclasses import dataclass

from rustprint.src.dependency_analyzer.utils.logging_config import setup_logging
setup_logging(level=logging.INFO)

logger = logging.getLogger(__name__)

from rustprint.src.llm_services import create_main_model
from rustprint.src.agent_tools.str_replace_editor import str_replace_editor_tool
from rustprint.src.agent_tools.find_code_component import find_code_component_tool
from rustprint.src.agent_tools.deps import RefinementDeps
from rustprint.src.agent_tools.maven_compile import maven_compile_tool
from rustprint.src.agent_tools.java_risk_detect import java_risk_detect_tool
from rustprint.src.config import Config
from rustprint.src.utils import file_manager


REFINEMENT_SYSTEM_PROMPT = """You are an expert Java code refinement agent.

<ROLE>
We have completed a comparison between C code documentation (official reference) and Java documentation (generated from translated Java code). The evaluation has identified mismatches between what the C documentation describes and what the Java implementation provides. Your task is to fix the Java code to match the requirements from the C documentation.
</ROLE>

<WORKFLOW_CONTEXT>
1. C code documentation (official reference) was analyzed
2. Java code was generated from C code
3. Documentation was generated from the Java code
4. Evaluation compared Java documentation vs C documentation and found mismatches
5. You are provided with evaluation reasoning that describes mismatches between C docs and Java docs
6. Your job: Fix the Java code based on these mismatches
</WORKFLOW_CONTEXT>

<CRITICAL_RULES>
- This phase is refinement only: fix existing Java code to align with C documentation. Do NOT translate new code from C or add new modules; only modify the existing Java codebase.
- Do NOT generate or add tests. Tests are generated in a separate phase afterward. Production code only.
- Production Java must remain standard-library-only. Do not add Lombok, Guava, Apache Commons, native bindings, code generators, or other production dependencies.
</CRITICAL_RULES>

<WHAT_YOU_RECEIVE>
1. Requirement hierarchy showing context
2. Evaluation reasoning describing the mismatch between C docs and Java docs
3. Evidence from documentation comparison
4. Current score vs expected weight
5. Access to Java codebase via str_replace_editor tool
</WHAT_YOU_RECEIVE>

<YOUR_RESPONSIBILITIES>
1. Read the evaluation reasoning to understand the mismatch between C and Java documentation
2. Use str_replace_editor to view the relevant Java source files (.java files)
3. Analyze the current Java implementation
4. Determine if the Java code actually needs changes:
   - If mismatch is due to documentation generation errors but code is correct → No changes needed
   - If Java code doesn't match C requirements → Fix the code
5. Modify Java records/classes/enums/methods/package structure as needed.
6. After each file create or edit, call java_risk_detect(module='<current_module_name>'), then maven_compile(working_dir='.'). Fix errors and risky patterns before continuing.
7. Ensure all changes are syntactically correct and idiomatic Java 17+: cohesive classes, records for pure data, encapsulated mutable state, no giant procedural utility class unless the module is truly stateless.
8. Adjust/create the .md files only when needed to keep documentation aligned with Java code changes.

</YOUR_RESPONSIBILITIES>

<CRITICAL_CONSTRAINTS>
- You can work with Java source files (.java) and Maven files (pom.xml) only when build configuration must change.
- You MUST use working_dir="rust_repo" for code operations; this is the legacy tool alias for the translated Java repository.
- If the Java code already matches the C documentation requirements, do nothing.
- Focus on alignment between Java implementation and C documentation.
- Strictly avoid sun.misc.Unsafe, jdk.internal.misc.Unsafe, JNI/native methods, System.exit, Runtime.exec, ProcessBuilder, and setAccessible(true) unless no Java translation is mathematically possible.
</CRITICAL_CONSTRAINTS>

<AVAILABLE_TOOLS>
You have full access to str_replace_editor tool with working_dir="rust_repo" (translated Java repository):

1. view: Read Java source files to understand current implementation
   str_replace_editor(command="view", working_dir="rust_repo", path="src/main/java/com/example/App.java")

2. str_replace: Modify existing code by replacing old code with new code
   str_replace_editor(
       command="str_replace",
       working_dir="rust_repo",
       path="src/main/java/com/example/Calculator.java",
       old_str="return x + 1;",
       new_str="return x + y;"
   )

3. insert: Add new code at a specific line number
   str_replace_editor(
       command="insert",
       working_dir="rust_repo",
       path="src/main/java/com/example/Calculator.java",
       insert_line=10,
       new_str="private int clamp(int value) {\\n    return Math.max(0, value);\\n}"
   )

4. create: Create new Java files
   str_replace_editor(
       command="create",
       working_dir="rust_repo",
       path="src/main/java/com/example/Point.java",
       file_text="package com.example;\\n\\npublic record Point(int x, int y) {}\\n"
   )

5. java_risk_detect(module='<current_module_name>'): Scan Java files for risky/non-portable patterns. Call after every file create or str_replace/insert.

6. maven_compile(working_dir='.'): Run Maven compile for the Java project. Call after java_risk_detect following every create/edit; fix errors and call again until "Done."

7. find_code_component(pattern, path_in_repo='.'):
    - Search inside the translated Java repository to find where symbols/snippets are implemented
    - Use this before view/str_replace when exact file path is unknown

Note: After every file create or edit, call in this order: (1) java_risk_detect(module='<current_module_name>'), (2) maven_compile(working_dir='.'). Do not accumulate edits without checking.
</AVAILABLE_TOOLS>

<IMPORTANT_DECISION_LOGIC>
1. Read evaluation reasoning carefully - it describes mismatch between C docs and Java docs
2. Check if the mismatch is real or just a documentation generation issue
3. If Java code already implements what C docs describe → Do nothing
4. If Java code differs from C docs → Fix the code
</IMPORTANT_DECISION_LOGIC>
"""
def _resolve_repo_dir(base: Path, name: str) -> Path:
    """Resolve repo directory; treat hyphen and underscore as equivalent (json-c vs json_c)."""
    for candidate in (name, name.replace("-", "_"), name.replace("_", "-")):
        p = base / candidate
        if p.is_dir():
            return p
    return base / name


class SketchRefinementOrchestrator:
    
    def __init__(self, config: Config, version: int, output_base_dir: str = "output"):
        self.config = config
        self.version = version
        self.next_version = version + 1
        self.model = create_main_model(config)

        # Resolve to absolute paths immediately
        self.base_dir = Path(output_base_dir).resolve()
        self.eval_dir = self.base_dir / "sketch_docs" / f"version_{version}"
        self.source_repo_dir = self.base_dir / "translated_repos" / f"version_{version}"
        self.target_repo_dir = self.base_dir / "translated_repos" / f"version_{self.next_version}"
        
        self.modified_files_log = {}
        
    def create_agent(self) -> Agent:
        return Agent(
            self.model,
            name="sketch_refinement_agent",
            deps_type=RefinementDeps,
            tools=[str_replace_editor_tool, java_risk_detect_tool, maven_compile_tool, find_code_component_tool],
            system_prompt=REFINEMENT_SYSTEM_PROMPT,
            retries=2,
            end_strategy='early',
        )
    
    def load_evaluation_results(self, repo_name: str) -> Dict[str, Any]:
        eval_repo = _resolve_repo_dir(self.eval_dir, repo_name)
        eval_file = eval_repo / "evaluation_results" / "combined_evaluation_results.json"
        
        if not eval_file.exists():
            raise FileNotFoundError(f"Evaluation results not found: {eval_file}")
        
        with open(eval_file, 'r') as f:
            return json.load(f)
    
    def extract_requirements_dfs(self, rubrics: List[Dict], parent_path: List[str] = None) -> List[Tuple[List[str], Dict]]:
        if parent_path is None:
            parent_path = []
        
        requirements = []
        
        for idx, item in enumerate(rubrics):
            current_path = parent_path + [item.get("requirements", f"Item_{idx}")]
            
            if "sub_tasks" in item and item["sub_tasks"]:
                child_requirements = self.extract_requirements_dfs(item["sub_tasks"], current_path)
                requirements.extend(child_requirements)
            else:
                requirements.append((current_path, item))
        
        return requirements
    
    def format_requirement_context(self, path: List[str], requirement: Dict) -> str:
        context = "="*80 + "\n"
        context += "REQUIREMENT HIERARCHY\n"
        context += "="*80 + "\n"
        for i, level in enumerate(path):
            indent = "  " * i
            context += f"{indent}→ {level}\n"
        
        context += "\n" + "="*80 + "\n"
        context += "CURRENT REQUIREMENT DETAILS\n"
        context += "="*80 + "\n"
        context += f"Name: {requirement.get('requirements', 'N/A')}\n"
        context += f"Weight: {requirement.get('weight', 'N/A')}\n"
        
        if "evaluation" in requirement:
            eval_data = requirement["evaluation"]
            context += f"Current Score: {eval_data.get('score', 0)}\n"
            context += f"\nEvaluation Reasoning:\n{eval_data.get('reasoning', 'N/A')}\n"
            context += f"\nEvidence from Documentation:\n{eval_data.get('evidence', 'N/A')}\n"
        
        context += "\n" + "="*80 + "\n"
        
        return context
    
    def should_skip_requirement(self, requirement: Dict) -> bool:
        """Check if a requirement should be skipped.
        
        A requirement should be skipped if:
        - It has no evaluation data
        - It has score == 1 (already passing)
        
        Returns True if should skip, False if should refine.
        """
        if "evaluation" not in requirement:
            return True
        
        score = requirement["evaluation"].get("score", 0)
        
        # Only refine requirements that failed (score == 0)
        return score != 0
    
    async def refine_for_requirement(self, repo_name: str, path: List[str], 
                                    requirement: Dict, agent: Agent) -> Tuple[bool, List[str]]:
        if self.should_skip_requirement(requirement):
            score = requirement["evaluation"].get("score", 0)
            weight = requirement.get("weight", 0)
            logger.info(f"✓ Skipping (score {score} == weight {weight}): {' -> '.join(path)}")
            return False, []
        
        score = requirement["evaluation"].get("score", 0)
        weight = requirement.get("weight", 0)
        
        logger.info("")
        logger.info("="*80)
        logger.info(f"REFINING REQUIREMENT: {' -> '.join(path)}")
        logger.info("="*80)
        logger.info(f"Score: {score} | Weight: {weight} | Gap: {abs(score - weight)}")
        logger.info(f"Repository: {repo_name}")
        logger.info(f"Target Path: {self.target_repo_dir / repo_name}")
        
        rust_workspace_path = str(self.target_repo_dir / repo_name)
        sketch_docs_path = str(self.eval_dir / repo_name)
        
        from rustprint.src.agent_tools.str_replace_editor import reset_view_history, get_modified_files
        reset_view_history()
        
        deps = RefinementDeps(
            rust_workspace_path=rust_workspace_path,
            sketch_docs_output_path=sketch_docs_path,
            current_module_name=repo_name,
            requirement_path=path,
            current_requirement=requirement,
            config=self.config
        )
        
        user_prompt = self.format_requirement_context(path, requirement)
        user_prompt += f"\nCurrent repo/module (use for java_risk_detect module parameter): {repo_name}\n"
        user_prompt += "\nTASK: Analyze the Java codebase and make necessary code changes to satisfy this requirement.\n"
        user_prompt += "Start by viewing relevant files to understand the current implementation. After each file create or edit, call java_risk_detect(module='"+repo_name+"'), then maven_compile(working_dir='.'); fix until Done.\n"
        
        try:
            logger.info("Starting agent refinement...")
            result = await run_agent_with_retry(agent, user_prompt, deps=deps, usage_limits=UsageLimits(request_limit=500))


            modified_files = get_modified_files()
            
            logger.info("="*80)
            logger.info(f"✓ Successfully refined: {' -> '.join(path)}")
            if modified_files:
                logger.info(f"  Modified files ({len(modified_files)}):")
                for file_path in modified_files:
                    logger.info(f"    - {file_path}")
            else:
                logger.info(f"  No files were modified (code already satisfies requirement)")
            logger.info("="*80)
            return True, modified_files
        except Exception as e:
            logger.error("="*80)
            logger.error(f"✗ Failed to refine {' -> '.join(path)}: {e}")
            logger.error("="*80)
            return False, []
    
    def copy_repository(self, repo_name: str) -> bool:
        """Copy repo from source to target. Returns True if copy was done, False if skipped (target exists)."""
        source = _resolve_repo_dir(self.source_repo_dir, repo_name)
        target = self.target_repo_dir / source.name
        
        if target.exists():
            logger.info(f"Target directory already exists: {target} — skipping repo (move to next)")
            return False
        
        logger.info(f"Copying repository from {source} to {target}")
        shutil.copytree(source, target)
        for cost_file in target.rglob("cost.json"):
            cost_file.unlink()
        for cost_file in target.rglob("cost.jsonl"):
            cost_file.unlink()
        logger.info(f"Repository copied successfully (cost files removed)")
        return True
    
    async def refine_repository(self, repo_name: str):
        overall_start = time.time()
        logger.info("\n" + "="*80)
        logger.info(f"RUST CODE REFINEMENT: {repo_name}")
        logger.info(f"Version: {self.version} → {self.next_version}")
        logger.info(f"Condition: Refine if score == 0 (failed)")
        logger.info("="*80)
        
        try:
            logger.info("Loading evaluation results...")
            eval_results = self.load_evaluation_results(repo_name)
            
            rubrics = eval_results.get("rubrics", [])
            if not rubrics:
                logger.error("No rubrics found in evaluation results")
                return
            
            logger.info("Extracting requirements in DFS order...")
            requirements = self.extract_requirements_dfs(rubrics)
            logger.info(f"Found {len(requirements)} leaf requirements to process")
            
            failed_reqs = [r for r in requirements if not self.should_skip_requirement(r[1])]
            logger.info(f"Requirements needing refinement (score == 0): {len(failed_reqs)}")
            
            if not failed_reqs:
                logger.info(f"All requirements passed (score == 1). No refinement needed.")
                return
            
            if not self.copy_repository(repo_name):
                return  # target already exists, skip this repo and move to next

            from pathlib import Path as _Path
            _target_repo = self.target_repo_dir / _resolve_repo_dir(self.source_repo_dir, repo_name).name

            resolved_source = _resolve_repo_dir(self.source_repo_dir, repo_name)
            resolved_repo_name = resolved_source.name
            agent = self.create_agent()
            
            logger.info("\n" + "="*80)
            logger.info("REFINEMENT PROCESS")
            logger.info("="*80)
            
            success_count = 0
            skip_count = 0
            fail_count = 0
            all_modified_files = []
            
            for idx, (path, requirement) in enumerate(requirements, 1):
                req_name = requirement.get('requirements', 'Unknown')
                score = requirement.get('evaluation', {}).get('score', 0) if 'evaluation' in requirement else 0
                weight = requirement.get('weight', 0)
                
                logger.info(f"\n{'─'*80}")
                logger.info(f"[{idx}/{len(requirements)}] {req_name}")
                logger.info(f"Path: {' -> '.join(path)}")
                logger.info(f"Score: {score} | Weight: {weight} | Status: {'SKIP' if score == 1 else 'REFINE'}")
                logger.info(f"{'─'*80}")
                
                if self.should_skip_requirement(requirement):
                    skip_count += 1
                    continue
                
                success, modified_files = await self.refine_for_requirement(resolved_repo_name, path, requirement, agent)
                
                if success:
                    success_count += 1
                    if modified_files:
                        for f in modified_files:
                            if f not in all_modified_files:
                                all_modified_files.append(f)
                        req_key = ' -> '.join(path)
                        self.modified_files_log[req_key] = modified_files
                else:
                    fail_count += 1
            
            overall_time = time.time() - overall_start
            
            logger.info("\n" + "="*80)
            logger.info("REFINEMENT COMPLETED")
            logger.info("="*80)
            logger.info(f"Repository: {repo_name}")
            logger.info(f"Total requirements: {len(requirements)}")
            logger.info(f"Skipped (score == 1): {skip_count}")
            logger.info(f"Refined successfully: {success_count}")
            logger.info(f"Failed: {fail_count}")
            logger.info(f"Total unique files modified: {len(all_modified_files)}")
            if all_modified_files:
                logger.info(f"\nModified files:")
                for file_path in all_modified_files:
                    logger.info(f"  - {file_path}")
            logger.info(f"Output: {self.target_repo_dir / repo_name}")
            logger.info(f"Total time: {overall_time:.2f}s")
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"Refinement failed for {repo_name}: {e}")
            raise
    
    async def refine_all_repositories(self):
        overall_start = time.time()
        logger.info("\n" + "="*80)
        logger.info("BATCH RUST CODE REFINEMENT")
        logger.info(f"Version: {self.version} → {self.next_version}")
        logger.info(f"Condition: Refine if score ≠ weight")
        logger.info("="*80)
        
        if not self.eval_dir.exists():
            logger.error(f"Evaluation directory not found: {self.eval_dir}")
            return
        
        repos = [d.name for d in self.eval_dir.iterdir() if d.is_dir()]
        
        if not repos:
            logger.error("No repositories found to refine")
            return
        
        logger.info(f"Found {len(repos)} repositories to refine")
        
        success_repos = []
        failed_repos = []
        
        for idx, repo_name in enumerate(repos, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Repository {idx}/{len(repos)}: {repo_name}")
            logger.info(f"{'='*80}")
            
            try:
                await self.refine_repository(repo_name)
                success_repos.append(repo_name)
            except Exception as e:
                logger.error(f"Failed to refine {repo_name}: {e}")
                failed_repos.append(repo_name)
        
        overall_time = time.time() - overall_start
        
        logger.info("\n" + "="*80)
        logger.info("BATCH REFINEMENT COMPLETED")
        logger.info("="*80)
        logger.info(f"Total repositories: {len(repos)}")
        logger.info(f"Successful: {len(success_repos)}")
        logger.info(f"Failed: {len(failed_repos)}")
        if failed_repos:
            logger.info(f"Failed repos: {', '.join(failed_repos)}")
        logger.info(f"Output directory: {self.target_repo_dir}")
        logger.info(f"Total time: {overall_time:.2f}s")
        logger.info("="*80)


async def main():
    """Main entry point for sketch refinement."""
    import argparse
    from rustprint.src.config import Config, LLM_BASE_URL, LLM_API_KEY

    parser = argparse.ArgumentParser(
        description='Refine Java code based on evaluation results'
    )
    parser.add_argument(
        '--version',
        type=int,
        required=True,
        help='Source version number to refine (e.g., 0, 1, 2)'
    )
    parser.add_argument(
        '--repo',
        type=str,
        default='',
        help='Specific repository to refine (default: all repos in version)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Base output directory (default: output)'
    )
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Model name to use (e.g., gpt-5.2, gpt-5.4, kimi-k2-instruct)'
    )

    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("="*80)
    logger.info("Java Code Refinement")
    logger.info("="*80)
    logger.info(f"Source Version: {args.version}")
    logger.info(f"Target Version: {args.version + 1}")
    logger.info(f"Repository: {args.repo if args.repo else 'All repositories'}")
    logger.info(f"Condition: Refine if score ≠ weight")
    logger.info(f"Model: {args.model}")
    logger.info("="*80)

    config = Config.for_llm_only(
        llm_base_url=LLM_BASE_URL,
        llm_api_key=LLM_API_KEY,
        model=args.model,
    )
    
    # Create refinement agent
    agent = SketchRefinementOrchestrator(config, version=args.version, output_base_dir=args.output_dir)
    
    # Run refinement
    if args.repo:
        await agent.refine_repository(args.repo)
    else:
        await agent.refine_all_repositories()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
