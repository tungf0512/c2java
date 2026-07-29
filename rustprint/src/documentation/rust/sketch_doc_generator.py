import logging
import os
import time
from typing import Dict, List, Any
from pydantic_ai import Agent, UsageLimits

logger = logging.getLogger(__name__)

from rustprint.src.agent_tools.deps import SketchDocDeps
from rustprint.src.agent_tools.str_replace_editor import str_replace_editor_tool, reset_view_history
from rustprint.src.agent_tools.find_code_component import find_code_component_tool
from rustprint.src.agent_tools.read_documentation import read_documentation_tool
from rustprint.src.llm_services import create_main_model, build_model_settings_dict
from rustprint.src.agent_retry import run_agent_with_retry
from rustprint.src.prompt_template import SKETCH_DOC_LEAF_PROMPT, SKETCH_DOC_PARENT_PROMPT
from rustprint.src.config import Config
from rustprint.src.utils import file_manager


class SketchDocGenerator:
    
    def __init__(self, config: Config):
        self.config = config
        self.model = create_main_model(config)

    def create_leaf_doc_agent(self) -> Agent:
        return Agent(
            self.model,
            name="SketchDoc_Leaf",
            deps_type=SketchDocDeps,
            tools=[
                str_replace_editor_tool,
                find_code_component_tool,
            ],
            system_prompt=SKETCH_DOC_LEAF_PROMPT,
            retries=2,
            end_strategy='early',
        )
    
    def create_parent_doc_agent(self) -> Agent:
        return Agent(
            self.model,
            name="SketchDoc_Parent",
            deps_type=SketchDocDeps,
            tools=[
                str_replace_editor_tool,
                read_documentation_tool,
                find_code_component_tool,
            ],
            system_prompt=SKETCH_DOC_PARENT_PROMPT,
            retries=2,
            end_strategy='early',
        )
    
    def get_processing_order(self, module_tree: Dict[str, Any], parent_path: List[str] = []) -> List[tuple[List[str], str, bool]]:
        processing_order = []
        
        def collect_modules(tree: Dict[str, Any], path: List[str]):
            for module_name, module_info in tree.items():
                current_path = path + [module_name]
                children = module_info.get("children", {})
                has_children = children and isinstance(children, dict) and len(children) > 0
                
                if has_children:
                    collect_modules(children, current_path)
                    processing_order.append((current_path, module_name, True))
                else:
                    processing_order.append((current_path, module_name, False))
        
        collect_modules(module_tree, parent_path)
        return processing_order
    
    async def generate_module_doc(
        self,
        module_name: str,
        is_parent: bool,
        rust_workspace_path: str,
        sketch_docs_output_path: str,
        deps: SketchDocDeps,
        leaf_agent: Agent,
        parent_agent: Agent,
        depth: int = 0
    ):
        start_time = time.time()
        indent = "  " * depth
        
        reset_view_history()
        
        logger.info(f"{indent}[Module: {module_name}] Type: {'Parent' if is_parent else 'Leaf'}")
        
        output_doc_path = os.path.join(sketch_docs_output_path, f"{module_name}.md")
        
        deps.current_module_name = module_name
        deps.rust_workspace_path = rust_workspace_path
        deps.sketch_docs_output_path = sketch_docs_output_path
        
        logger.info(f"{indent}  Java/Maven workspace: {rust_workspace_path}")
        logger.info(f"{indent}  Output: {output_doc_path}")
        
        if is_parent:
            logger.info(f"{indent}  [Parent Agent] Generating documentation with children context...")
            
            children_docs = []
            for file in os.listdir(sketch_docs_output_path):
                if file.endswith('.md') and file != f"{module_name}.md" and file != "overview.md":
                    children_docs.append(file.replace('.md', ''))
            
            prompt = f"""Generate high-level feature-focused documentation for the Java module '{module_name}'.

This module is located in the Java/Maven workspace. You need to explore and find the correct package/module folder that corresponds to this module.
For example, if documenting 'child' module under 'parent', look for the folder at parent/child.

Children modules documentation available: {', '.join(children_docs) if children_docs else 'None'}

Your task:
1. Explore the Java/Maven workspace to find the package/module folder for module '{module_name}'
2. Read the Java code in that module folder under src/main/java
3. Read children module documentation using read_documentation tool to understand their features
4. Identify the HIGH-LEVEL FEATURES this module provides
5. Generate feature-focused documentation (NOT function listings)
6. Create the file: {output_doc_path}

IMPORTANT: Focus on FEATURES (capabilities and functionality), not individual function listings.
Document what the module enables users to do, how children modules contribute to features, and how components integrate.
"""
            
            result = await run_agent_with_retry(
                parent_agent,
                prompt,
                deps=deps,
                message_history=None,
                model_settings=build_model_settings_dict(self.config.main_model, 0.0, 16000),
                usage_limits=UsageLimits(request_limit=500)
            )
        else:
            logger.info(f"{indent}  [Leaf Agent] Generating documentation from workspace...")
            
            prompt = f"""Generate high-level feature-focused documentation for the Java module '{module_name}'.

This module is located in the Java/Maven workspace. You need to explore and find the correct package/module folder that corresponds to this module.
For example, if documenting 'child' module under 'parent', look for the folder at parent/child.

Your task:
1. Explore the Java/Maven workspace to find the package/module folder for module '{module_name}'
2. Read all Java source files in that module folder under src/main/java
3. Identify the HIGH-LEVEL FEATURES this module provides
4. Generate feature-focused documentation (NOT function listings)
5. Create the file: {output_doc_path}

IMPORTANT: Focus on FEATURES (capabilities and functionality), not individual function listings.
Document what the module enables users to do and how features work conceptually.
"""
            
            result = await run_agent_with_retry(
                leaf_agent,
                prompt,
                deps=deps,
                message_history=None,
                model_settings=build_model_settings_dict(self.config.main_model, 0.0, 16000),
                usage_limits=UsageLimits(request_limit=500)
            )

        elapsed = time.time() - start_time
        
        if os.path.exists(output_doc_path):
            logger.info(f"{indent}  Documentation created: {output_doc_path} ({elapsed:.1f}s)")
        else:
            logger.warning(f"{indent}  Documentation not created ({elapsed:.1f}s) - Forcing generation with available information")
            
            force_prompt = f"""CRITICAL: You must generate documentation NOW with the information you have already gathered.

You have explored the Java module '{module_name}' but did not create the documentation file yet.

IMMEDIATE ACTION REQUIRED:
1. Use ALL the information you have gathered from your exploration
2. Generate documentation based on what you were able to read
3. If you couldn't find all files, document what you DID find
4. Create the file: {output_doc_path}

Even partial documentation is better than no documentation. Generate it NOW using:
str_replace_editor(working_dir='rust_doc', command='create', path='./{module_name}.md', file_text='...')
"""
            
            try:
                retry_result = await run_agent_with_retry(
                    parent_agent if is_parent else leaf_agent,
                    force_prompt,
                    deps=deps,
                    message_history=result.all_messages() if hasattr(result, 'all_messages') else None,
                    model_settings=build_model_settings_dict(self.config.main_model, 0.0, 8000),
                    usage_limits=UsageLimits(request_limit=500)
                )

                if os.path.exists(output_doc_path):
                    logger.info(f"{indent}  Documentation created after retry: {output_doc_path}")
                else:
                    logger.error(f"{indent}  Failed to create documentation even after retry")
            except Exception as e:
                logger.error(f"{indent}  Retry failed with error: {e}")
        
        return result
    
    async def generate_documentation(
        self,
        repo_name: str,
        c_docs_path: str,
        rust_translated_path: str,
        output_sketch_docs_path: str
    ):
        logger.info("="*80)
        logger.info("SKETCH DOCUMENTATION GENERATION")
        logger.info("="*80)
        logger.info(f"Repo: {repo_name}")
        logger.info(f"C docs: {c_docs_path}")
        logger.info(f"Java translated: {rust_translated_path}")
        logger.info(f"Output: {output_sketch_docs_path}")
        logger.info("="*80)
        
        file_manager.ensure_directory(output_sketch_docs_path)

        from pathlib import Path

        module_tree_path = os.path.join(c_docs_path, "module_tree.json")
        module_tree = None
        
        if os.path.exists(module_tree_path):
            module_tree = file_manager.load_json(module_tree_path)
        
        files_created = []  # Track created files
        
        # Helper to create ultimate fallback documentation
        def create_ultimate_fallback():
            """Create a basic fallback markdown file if all else fails."""
            fallback_path = os.path.join(output_sketch_docs_path, "overview.md")
            try:
                # Scan the Java workspace for basic info
                workspace_info = []
                try:
                    for root, dirs, files in os.walk(rust_translated_path):
                        for f in files:
                            if f.endswith('.java') or f == 'pom.xml' or f == 'README.md':
                                rel_path = os.path.relpath(os.path.join(root, f), rust_translated_path)
                                workspace_info.append(rel_path)
                        if len(workspace_info) > 50:
                            break
                except Exception as e:
                    logger.warning(f"Could not scan workspace: {e}")
                
                fallback_content = f"""# {repo_name} - Repository Overview

*Auto-generated fallback documentation*

## Repository Information
- **Repository**: {repo_name}
- **Java Workspace**: {rust_translated_path}
- **Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Workspace Structure
The following files were discovered in the Java/Maven workspace:

"""
                if workspace_info:
                    for info in workspace_info[:100]:
                        fallback_content += f"- `{info}`\n"
                    if len(workspace_info) > 100:
                        fallback_content += f"\n... and {len(workspace_info) - 100} more files\n"
                else:
                    fallback_content += "*No Java/Maven files found in workspace.*\n"
                
                fallback_content += f"""

## Note
This is a fallback documentation generated because the LLM-based documentation generation failed to produce output. Please refer to the source code directly for detailed information.

## Maven Project
"""
                # Try to read pom.xml for basic info
                pom_path = os.path.join(rust_translated_path, "pom.xml")
                if os.path.exists(pom_path):
                    try:
                        with open(pom_path, 'r') as f:
                            pom_content = f.read()[:2000]
                        fallback_content += f"\n```xml\n{pom_content}\n```\n"
                    except Exception:
                        pass
                
                with open(fallback_path, 'w') as f:
                    f.write(fallback_content)
                
                logger.warning(f"Created ultimate fallback documentation: {fallback_path}")
                return [fallback_path]
            except Exception as e:
                logger.error(f"Even ultimate fallback failed: {e}")
                # Last resort - create empty file to prevent pipeline failure
                try:
                    with open(fallback_path, 'w') as f:
                        f.write(f"# {repo_name}\n\nDocumentation generation failed completely.\n")
                    return [fallback_path]
                except Exception:
                    return []
            return []
        
        module_tree_path = os.path.join(c_docs_path, "module_tree.json")
        module_tree = None
        
        if os.path.exists(module_tree_path):
            module_tree = file_manager.load_json(module_tree_path)
        
        if not module_tree:
            logger.warning("Module tree not found or empty - will generate overview from entire Java/Maven workspace")
            logger.info("Scanning Java/Maven workspace to discover structure...")
            
            leaf_agent = self.create_leaf_doc_agent()
            parent_agent = self.create_parent_doc_agent()
            
            deps = SketchDocDeps(
                current_module_name="overview",
                rust_workspace_path=rust_translated_path,
                sketch_docs_output_path=output_sketch_docs_path,
            )
            
            overview_output = os.path.join(output_sketch_docs_path, "overview.md")
            
            reset_view_history()
            
            logger.info("\n[Overview] Generating repository overview from entire Java/Maven workspace...")
            
            prompt = f"""Generate comprehensive high-level feature-focused repository overview documentation by exploring the entire Java/Maven workspace.

Java/Maven workspace: {rust_translated_path}

Your task:
1. Explore the entire Java/Maven workspace structure using str_replace_editor(working_dir='rust_repo', command='view')
   - Read pom.xml files to understand Maven modules and dependencies
   - Read README.md (if exists) to understand project purpose
   - Explore src/main/java directories and Java source files to discover modules and features
2. Identify all major features and capabilities provided by this Java repository
3. Understand how different modules/components work together
4. Synthesize a HIGH-LEVEL overview of repository features
5. Create the file: {overview_output}

IMPORTANT: 
- Focus on repository-level FEATURES and capabilities, not file-by-file listings
- Document what the repository enables, key feature areas, and how components integrate
- Include architecture diagrams (Mermaid) showing feature flows and component interactions
- If you find multiple Maven modules/packages, document how they relate and work together
"""
            
            _overview_result = await run_agent_with_retry(
                parent_agent,
                prompt,
                deps=deps,
                message_history=None,
                model_settings=build_model_settings_dict(self.config.main_model, 0.0, 16000),
                usage_limits=UsageLimits(request_limit=500)
            )

            if os.path.exists(overview_output):
                logger.info(f"  Overview created: {overview_output}")
                files_created.append(overview_output)
            else:
                logger.warning("  Overview generation failed - will use fallback")
                files_created.extend(create_ultimate_fallback())
            
            # Ensure at least one file exists
            if not files_created:
                logger.warning("No files created by agent - using ultimate fallback")
                files_created.extend(create_ultimate_fallback())
            
            logger.info("\n" + "="*80)
            logger.info("SKETCH DOCUMENTATION GENERATION COMPLETED")
            logger.info("="*80)
            return
        
        logger.info(f"Loaded module tree with {len(module_tree)} top-level modules")
        
        processing_order = self.get_processing_order(module_tree)
        logger.info(f"Processing order: {len(processing_order)} modules (bottom-up)")
        
        leaf_agent = self.create_leaf_doc_agent()
        parent_agent = self.create_parent_doc_agent()
        
        deps = SketchDocDeps(
            current_module_name="",
            rust_workspace_path="",
            sketch_docs_output_path=output_sketch_docs_path,
        )
        
        for idx, (module_path, module_name, is_parent) in enumerate(processing_order, 1):
            logger.info(f"\n[{idx}/{len(processing_order)}] Processing: {module_name}")
            
            result = await self.generate_module_doc(
                module_name=module_name,
                is_parent=is_parent,
                rust_workspace_path=rust_translated_path,
                sketch_docs_output_path=output_sketch_docs_path,
                deps=deps,
                leaf_agent=leaf_agent,
                parent_agent=parent_agent,
                depth=len(module_path) - 1
            )
            
            # Track created files
            output_doc_path = os.path.join(output_sketch_docs_path, f"{module_name}.md")
            if os.path.exists(output_doc_path):
                files_created.append(output_doc_path)
        
        # Generate overview
        overview_output = os.path.join(output_sketch_docs_path, "overview.md")
        
        reset_view_history()
        
        logger.info("\n[Overview] Generating repository overview...")
        deps.current_module_name = "overview"
        deps.rust_workspace_path = rust_translated_path
        
        generated_docs = []
        for file in os.listdir(output_sketch_docs_path):
            if file.endswith('.md'):
                generated_docs.append(file.replace('.md', ''))
        
        prompt = f"""Generate high-level feature-focused repository overview documentation.

Java/Maven workspace: {rust_translated_path}
Generated module documentation: {', '.join(generated_docs) if generated_docs else 'None'}

Your task:
1. Read generated module documentation using read_documentation tool to understand features
2. Read the root Java/Maven workspace (pom.xml, README.md) if needed using str_replace_editor
3. Synthesize a HIGH-LEVEL overview of repository features
4. Create the file: {overview_output}

IMPORTANT: Focus on repository-level FEATURES and capabilities, not module-by-module listings.
Document what the repository enables, key feature areas, and how modules integrate to provide functionality.
"""
        
        _final_overview_result = await run_agent_with_retry(
            parent_agent,
            prompt,
            deps=deps,
            message_history=None,
            model_settings=build_model_settings_dict(self.config.main_model, 0.0, 16000),
            usage_limits=UsageLimits(request_limit=500)
        )

        if os.path.exists(overview_output):
            logger.info(f"  Overview created: {overview_output}")
            files_created.append(overview_output)
        else:
            logger.warning("  Overview generation failed")
        
        # ULTIMATE FALLBACK: If no files were created at all, create a basic fallback
        if not files_created:
            logger.warning("No markdown files were created by agents - creating ultimate fallback documentation")
            files_created.extend(create_ultimate_fallback())
        
        logger.info(f"\nTotal markdown files created: {len(files_created)}")
        for f in files_created:
            logger.info(f"  - {os.path.basename(f)}")
        
        logger.info("\n" + "="*80)
        logger.info("SKETCH DOCUMENTATION GENERATION COMPLETED")
        logger.info("="*80)
