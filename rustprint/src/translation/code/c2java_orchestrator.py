from pydantic_ai import Agent, UsageLimits
import logging
import os
import time
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

pydantic_logger = logging.getLogger('pydantic_ai')
pydantic_logger.setLevel(logging.DEBUG)

MAX_REQUESTS_PLANNER = 500
MAX_REQUESTS_SKELETON = 500
MAX_REQUESTS_SYNTHESIS = 500

def log_info(msg: str, func_name: str = ""):
    if func_name:
        logger.info(f"[{func_name} @ c2java_orchestrator.py] {msg}")
    else:
        logger.info(msg)

from rustprint.src.agent_tools.deps import C2RustDeps
from rustprint.src.agent_tools.read_code_components import read_code_components_tool
from rustprint.src.agent_tools.str_replace_editor import str_replace_editor_tool
from rustprint.src.agent_tools.read_documentation import read_documentation_tool
from rustprint.src.agent_tools.find_code_component import find_code_component_tool
from rustprint.src.agent_tools.maven_compile import maven_compile_tool
from rustprint.src.agent_tools.java_risk_detect import java_risk_detect_tool
from rustprint.src.llm_services import create_main_model
from rustprint.src.agent_retry import run_agent_with_retry
from rustprint.src.prompt_template import PLANNER_PROMPT, SKELETON_PROMPT, SYNTHESIS_PROMPT
from rustprint.src.config import Config


class C2JavaOrchestrator:
    
    def __init__(self, config: Config):
        self.config = config
        self.model = create_main_model(config)

    def create_planner_agent(self) -> Agent:
        """Planner creates IMPLEMENTATION_PLAN.md for each feature"""
        return Agent(
            self.model,
            name="C2Java_Planner",
            deps_type=C2RustDeps,
            tools=[
                read_code_components_tool,
                str_replace_editor_tool,
                read_documentation_tool,
                find_code_component_tool,
            ],
            system_prompt=PLANNER_PROMPT,
            retries=2,
            end_strategy='early',
        )
    
    def create_skeleton_agent(self) -> Agent:
        """Skeleton reads plan and generates Java code."""
        return Agent(
            self.model,
            name="C2Java_Skeleton",
            deps_type=C2RustDeps,
            tools=[
                read_code_components_tool,
                str_replace_editor_tool,
                read_documentation_tool,
                find_code_component_tool,
                maven_compile_tool,
                java_risk_detect_tool,
            ],
            system_prompt=SKELETON_PROMPT,
            retries=2,
            end_strategy='early',
        )
    
    def create_synthesis_agent(self) -> Agent:
        return Agent(
            self.model,
            name="C2Java_Synthesis",
            deps_type=C2RustDeps,
            tools=[
                str_replace_editor_tool,
                find_code_component_tool,
                maven_compile_tool,
            ],
            system_prompt=SYNTHESIS_PROMPT,
            end_strategy='early',
        )
    
    def create_all_folders(
        self,
        module_tree: Dict[str, Any],
        parent_path: str,
        depth: int = 0,
        repo_name: Optional[str] = None,
    ):
        if repo_name and len(module_tree) == 1 and next(iter(module_tree.keys())) == repo_name:
            log_info("Single Java project at root: no subfolder created", "create_all_folders")
            return
        for feature_name, feature_info in module_tree.items():
            feature_path = os.path.join(parent_path, feature_name)
            os.makedirs(feature_path, exist_ok=True)
            log_info(f"Created: {feature_name}/", "create_all_folders")
    
    async def process_feature_recursive(
        self,
        feature_name: str,
        feature_info: Dict[str, Any],
        parent_path: str,
        deps: C2RustDeps,
        planner: Agent,
        skeleton_agent: Agent,
        depth: int = 0,
        output_path_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        BOTTOM-UP processing: Process children first, then parent.
        When output_path_override is set (e.g. single Maven project at root), use it as feature_output_path.
        """
        feature_start = time.time()
        indent = "  " * depth
        
        feature_output_path = output_path_override if output_path_override else os.path.join(parent_path, feature_name)
        feature_components = feature_info.get("components", [])
        feature_children = feature_info.get("children", {})
        
        log_info(f"{indent}[Feature] {feature_name}", "process_feature_recursive")
        log_info(f"{indent}  Components: {len(feature_components)}, Children: {len(feature_children)}", "process_feature_recursive")
        log_info(f"{indent}  Output: {feature_output_path}", "process_feature_recursive")
        
        deps.current_module = feature_name
        deps.absolute_rust_output_path = feature_output_path
        # Legacy deps field: current Maven module root for this feature.
        deps.current_crate_root = feature_output_path if depth == 0 else parent_path

        component_list = "\n".join([f"  - {comp_id}" for comp_id in feature_components])

        doc_files_list = ["overview.md", f"{feature_name}.md"]
        for child_name in feature_children.keys():
            doc_files_list.append(f"{child_name}.md")
        
        doc_files_info = "\n".join([f"  - {doc}" for doc in doc_files_list])
        
        planner_start = time.time()
        log_info(f"{indent}  [Phase 1: Planner] Creating implementation plan...", "process_feature_recursive")
        
        plan_path = os.path.join(feature_output_path, "IMPLEMENTATION_PLAN.md")
        max_planner_attempts = 3
        plan_created = False
        
        for attempt in range(1, max_planner_attempts + 1):
            if attempt > 1:
                log_info(f"{indent}  [Retry {attempt}/{max_planner_attempts}] Attempting to create plan...", "process_feature_recursive")
            
            planner_prompt = f"""
Create a comprehensive implementation plan file named IMPLEMENTATION_PLAN.md for translating the C module '{feature_name}' to Java.

<MODULE_INFO>
Module Name: {feature_name}
C Components: {len(feature_components)}
Children Modules: {len(feature_children)}
Output Directory: {feature_output_path}
</MODULE_INFO>

<C_COMPONENTS>
{component_list}
</C_COMPONENTS>

<DOCUMENTATION_FILES>
Available documentation in c_docs:
{doc_files_info}
</DOCUMENTATION_FILES>
"""
            
            try:
                planner_result = await run_agent_with_retry(
                    planner,
                    planner_prompt,
                    deps=deps,
                    message_history=None,
                    usage_limits=UsageLimits(request_limit=MAX_REQUESTS_PLANNER)
                )


                if os.path.exists(plan_path):
                    plan_created = True
                    log_info(f"{indent}  ✓ IMPLEMENTATION_PLAN.md created", "process_feature_recursive")
                    break
                else:
                    log_info(f"{indent}  ⚠ Attempt {attempt}: Plan not created", "process_feature_recursive")
                    if attempt < max_planner_attempts:
                        log_info(f"{indent}    Agent may have only analyzed code. Retrying with stronger instruction...", "process_feature_recursive")
            except Exception as e:
                log_info(f"{indent}  ⚠ Attempt {attempt} failed: {str(e)}", "process_feature_recursive")
        
        planner_time = time.time() - planner_start
        log_info(f"{indent}  Planner completed in {planner_time:.2f}s", "process_feature_recursive")
        
        if not plan_created:
            log_info(f"{indent}  ⚠ Planner did not create IMPLEMENTATION_PLAN.md; writing fallback Java plan", "process_feature_recursive")
            os.makedirs(feature_output_path, exist_ok=True)
            with open(plan_path, "w", encoding="utf-8") as handle:
                handle.write(f"""# Implementation Plan: {feature_name}

Translate the C components below into an idiomatic Java 17 Maven project.

## Required project structure

- `pom.xml`
- `src/main/java/...`
- `src/test/java/...` only if tests are part of this translation stage

## Java mapping rules

- Represent pure C structs as Java records when they only carry data.
- Implement C functions as cohesive static methods or instance methods on small domain classes.
- Use only the Java standard library in production code.
- Do not use JNI, `sun.misc.Unsafe`, `Runtime.exec`, `ProcessBuilder`, or heavy reflection.

## Components to translate

{component_list or "- No explicit components were listed; inspect the C repository and documentation."}

## Validation

Run `maven_compile` after creating the Java files and fix any compiler diagnostics.
""")
            plan_created = True
        
        skeleton_start = time.time()
        log_info(f"{indent}  [Phase 2: Implementation] Generating Java code...", "process_feature_recursive")
        with open(plan_path, "r", encoding="utf-8") as handle:
            plan_text = handle.read().strip()
        
        skeleton_prompt = f"""
Implement Java code for module '{feature_name}' following IMPLEMENTATION_PLAN.md specifications.

<OUTPUT_PATH>
{feature_output_path}
</OUTPUT_PATH>

<IMPLEMENTATION_PLAN_CONTENT>
{plan_text}
</IMPLEMENTATION_PLAN_CONTENT>

<MANDATORY_OUTPUT>
You MUST create a compilable Maven Java project in the output path using `str_replace_editor`.
At minimum, create:
- `pom.xml`
- one or more production `.java` files under `src/main/java/...`

For this phase, do not merely describe the implementation. Create the files.
After creating files, call `maven_compile` with working_dir='rust_repo' and fix any compiler errors.
</MANDATORY_OUTPUT>

"""
        
        skeleton_result = await run_agent_with_retry(
            skeleton_agent,
            skeleton_prompt,
            deps=deps,
            message_history=None,
            usage_limits=UsageLimits(request_limit=MAX_REQUESTS_SKELETON)
        )


        skeleton_time = time.time() - skeleton_start
        log_info(f"{indent}  Implementation completed in {skeleton_time:.2f}s", "process_feature_recursive")
        
        # Show what was created
        created_files = []
        if os.path.exists(feature_output_path):
            for root, dirs, files in os.walk(feature_output_path):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), feature_output_path)
                    created_files.append(rel_path)
            
            if created_files:
                log_info(f"{indent}  Created {len(created_files)} files:", "process_feature_recursive")
                for f in sorted(created_files)[:15]:
                    log_info(f"{indent}    - {f}", "process_feature_recursive")
                if len(created_files) > 15:
                    log_info(f"{indent}    ... and {len(created_files) - 15} more", "process_feature_recursive")
            else:
                log_info(f"{indent}  ⚠ WARNING: No files created!", "process_feature_recursive")

        # FALLBACK: If no Java files created, generate basic fallback files
        if depth == 0 and not any(f == "pom.xml" or f.endswith(".java") for f in created_files):
            log_info(f"{indent}  ⚠ No Java files generated by model - creating fallback implementation", "process_feature_recursive")
            created_files = self._create_fallback_java(feature_name, feature_output_path)
            
            # Re-check created files
            if created_files:
                log_info(f"{indent}  Fallback created {len(created_files)} files:", "process_feature_recursive")
                for f in sorted(created_files)[:15]:
                    log_info(f"{indent}    - {f}", "process_feature_recursive")
        
        feature_time = time.time() - feature_start
        
        result = {
            "output_path": feature_output_path,
            "has_children": len(feature_children) > 0,
            "children_results": {},
            "timing": {"planner": planner_time, "skeleton": skeleton_time}
        }
        
        log_info(f"{indent}✓ {feature_name} complete (total: {feature_time:.2f}s)", "process_feature_recursive")
        return result
    
    def _create_fallback_java(self, feature_name: str, feature_output_path: str) -> List[str]:
        """Create minimal fallback Java files when the model fails to generate code."""
        import traceback
        created_files = []
        
        try:
            # Ensure directory structure exists
            src_main_java = os.path.join(feature_output_path, "src", "main", "java")
            os.makedirs(src_main_java, exist_ok=True)
            
            # Create pom.xml
            pom_path = os.path.join(feature_output_path, "pom.xml")
            if not os.path.exists(pom_path):
                pom_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.migration.generated</groupId>
    <artifactId>{feature_name.lower()}</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>jar</packaging>
    
    <name>{feature_name} - Fallback Translation</name>
    <description>Auto-generated fallback Java translation for {feature_name}</description>
    
    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.0</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>17</source>
                    <target>17</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
'''
                with open(pom_path, 'w') as f:
                    f.write(pom_content)
                created_files.append("pom.xml")
            
            # Create a basic Java class
            # Extract package name from feature name
            base_package = "com.migration.generated"
            if "." in feature_name:
                base_package = feature_name.lower()
            elif feature_name != feature_name.lower():
                base_package = f"com.migration.generated.{feature_name.lower()}"
            
            # Create package directory
            package_dir = os.path.join(src_main_java, *base_package.split("."))
            os.makedirs(package_dir, exist_ok=True)
            
            # Create main class
            class_name = feature_name.replace("-", "").replace("_", "").capitalize()
            if not class_name[0].isalpha():
                class_name = "Generated" + class_name
            
            java_file = os.path.join(package_dir, f"{class_name}.java")
            java_content = f'''package {base_package};

/**
 * Fallback implementation for {feature_name}
 * This class was auto-generated when the translation model failed to produce output.
 * Replace with proper C-to-Java translation.
 */
public class {class_name} {{
    
    /**
     * Placeholder method - replace with actual implementation
     */
    public String process(String input) {{
        // TODO: Implement actual C-to-Java translation logic
        return "Processed: " + input;
    }}
    
    /**
     * Placeholder for data processing
     */
    public Map<String, Object> getMetadata() {{
        return Map.of(
            "class", "{class_name}",
            "feature", "{feature_name}",
            "generated", true,
            "fallback", true
        );
    }}
}}
'''
            with open(java_file, 'w') as f:
                f.write(java_content)
            created_files.append(f"src/main/java/{base_package.replace('.', '/')}/{class_name}.java")
            
            # Create a basic README
            readme_path = os.path.join(feature_output_path, "README.md")
            if not os.path.exists(readme_path):
                with open(readme_path, 'w') as f:
                    f.write(f'''# {feature_name.capitalize()} - Java Translation

This is a fallback Java implementation generated when the primary translation model failed to produce output.

## Build
```bash
mvn compile
```

## Note
This is a fallback implementation. The actual C-to-Java translation should replace these stub classes with proper translations of the original C logic.
''')
                created_files.append("README.md")
            
            return created_files
            
        except Exception as e:
            print(f"  [Fallback] Error creating fallback Java: {e}")
            traceback.print_exc()
            return []
    
    async def translate_module(
        self,
        c_repo_path: str,
        docs_path: str,
        components: Dict[str, Any],
        top_files: Dict[str, Any],
        module_tree: Dict[str, Any],
        output_dir: str
    ) -> C2RustDeps:
        
        translation_start = time.time()
        
        repo_name = os.path.basename(os.path.normpath(c_repo_path))
        # Output directory should already include the full path
        # Don't add extra 'translated_repos' folder
        java_output_path = os.path.join(output_dir, repo_name)
        os.makedirs(java_output_path, exist_ok=True)

        from pathlib import Path

        log_info(f"Initializing Java translation for: {repo_name}", "translate_module")
        log_info(f"   C source: {c_repo_path}", "translate_module")
        log_info(f"   Documentation: {docs_path}", "translate_module")
        log_info(f"   Java output: {java_output_path}", "translate_module")
        log_info(f"   Modules to translate: {len(module_tree)}", "translate_module")
        
        deps = C2RustDeps(
            absolute_c_repo_path=c_repo_path,
            absolute_rust_output_path=java_output_path,
            absolute_docs_path=docs_path,
            registry=top_files,
            components=components,
            translation_plan={},
            current_module="",
            completed_steps=[],
            config=self.config,
        )
        
        logger.info("\n" + "─"*80)
        logger.info("Starting Java code generation workflow")
        logger.info("  Step 1: Planner - Creates IMPLEMENTATION_PLAN.md from docs")
        logger.info("  Step 2: Implementation - Generates actual Java code from plan")
        logger.info("  Folder structure: Top-level only (sub-folders created by agent)")
        logger.info("─"*80)
        
        logger.info("\n📁 Creating top-level folder structure...")
        self.create_all_folders(module_tree, java_output_path, repo_name=repo_name)
        logger.info("✓ Top-level folders created\n")
        
        planner = self.create_planner_agent()
        skeleton_agent = self.create_skeleton_agent()
        synthesis_agent = self.create_synthesis_agent()
        
        feature_results = {}
        all_timings = []
        
        single_module_at_root = len(module_tree) == 1 and next(iter(module_tree.keys())) == repo_name
        deps.single_crate_at_root = single_module_at_root
        for feature_idx, (feature_name, feature_info) in enumerate(module_tree.items(), 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Feature [{feature_idx}/{len(module_tree)}]: {feature_name}")
            logger.info(f"{'='*80}")
            out_override = java_output_path if single_module_at_root else None
            result = await self.process_feature_recursive(
                feature_name,
                feature_info,
                java_output_path,
                deps,
                planner,
                skeleton_agent,
                depth=0,
                output_path_override=out_override,
            )
            
            feature_results[feature_name] = result
            all_timings.append({
                "feature": feature_name,
                "time": result.get("timing", {}).get("total", 0)
            })
            
            logger.info(f"\nFeature {feature_idx}/{len(module_tree)} completed: {feature_name}")
            if result['has_children']:
                logger.info(f"   Children processed: {len(result['children_results'])}")
        
        features_time = time.time() - translation_start
        
        logger.info("\n" + "="*80)
        logger.info("Starting ROOT workspace synthesis")
        logger.info("="*80)
        
        synthesis_start = time.time()
        
        logger.info(f"Features to synthesize: {len(feature_results)}")
        logger.info(f"Workspace directory: {java_output_path}")
        
        deps.absolute_rust_output_path = java_output_path
        deps.current_module = repo_name
        
        module_names = list(module_tree.keys())
        module_list_xml = "\n".join(f"    <module>{m}</module>" for m in module_names)
        if single_module_at_root:
            synthesis_prompt = f"""
Single-module Java project '{repo_name}': the Maven project is already at the repo root (pom.xml and src/main/java were created by the implementation step). Do NOT create a nested module. Verify the root pom.xml exists, then create README.md (project overview, build: mvn test) and .gitignore (target/). Use str_replace_editor with working_dir='rust_repo' to create ./README.md and ./.gitignore only.
"""
        else:
            synthesis_prompt = f"""
Create ROOT Maven aggregator files for translated Java project '{repo_name}'.

<PARAMETER>
module_names (from module_tree): [{', '.join(module_names)}]
</PARAMETER>

<CONTEXT>
Workspace ROOT directory: {java_output_path}
</CONTEXT>

For each module in the parameter list above, cd into that folder: use view with paths like ./<module_name>/pom.xml, ./<module_name>/README.md, ./<module_name>/src/main/java. Read each module's files once, then create root pom.xml with <packaging>pom</packaging> and <modules>, README.md, and .gitignore. Do NOT view path='.' repeatedly.
"""

        try:
            synthesis_result = await run_agent_with_retry(
                synthesis_agent,
                synthesis_prompt,
                deps=deps,
                message_history=None,
                usage_limits=UsageLimits(request_limit=MAX_REQUESTS_SYNTHESIS)
            )
            synthesis_time = time.time() - synthesis_start


            logger.info(f"Workspace synthesis completed ({synthesis_time:.2f}s)")
        except Exception as e:
            synthesis_time = time.time() - synthesis_start
            error_msg = str(e)
            logger.warning(f"Workspace synthesis exceeded limit ({synthesis_time:.2f}s): {error_msg}")

            if "request_limit" in error_msg.lower() or "usage" in error_msg.lower():
                if single_module_at_root:
                    logger.info("Single Java project at root: creating README and .gitignore only...")
                    try:
                        readme_path = os.path.join(java_output_path, "README.md")
                        if not os.path.exists(readme_path):
                            with open(readme_path, 'w') as f:
                                f.write(f"""# {repo_name}

Java translation of {repo_name} C repository.

## Build

```bash
mvn test
```
""")
                            logger.info("✓ Created README.md")
                        gitignore_path = os.path.join(java_output_path, ".gitignore")
                        if not os.path.exists(gitignore_path):
                            with open(gitignore_path, 'w') as f:
                                f.write("target/\n")
                            logger.info("✓ Created .gitignore")
                    except Exception as fallback_error:
                        logger.error(f"Failed to create fallback files: {str(fallback_error)}")
                else:
                    logger.info("Using agent's exploration history to create workspace files...")
                    force_create_prompt = f"""
You have explored the workspace features. Now CREATE the workspace files based on what you've seen.

DO NOT explore more. Just CREATE these files:

1. Create ./pom.xml:
   ```xml
   <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
     <modelVersion>4.0.0</modelVersion>
     <groupId>translated</groupId>
     <artifactId>{repo_name}</artifactId>
     <version>1.0-SNAPSHOT</version>
     <packaging>pom</packaging>
     <modules>
{module_list_xml}
     </modules>
   </project>
   ```

2. Create ./README.md:
   - Project: {repo_name}
   - Modules: {', '.join(module_names)}
   - Build: mvn test

3. Create ./.gitignore:
   ```
   target/
   ```

Use str_replace_editor with working_dir='rust_repo' to CREATE these 3 files NOW.
"""
                    try:
                        synthesis_result = await run_agent_with_retry(
                            synthesis_agent,
                            force_create_prompt,
                            deps=deps,
                            message_history=synthesis_agent._result_schema if hasattr(synthesis_agent, '_result_schema') else None,
                            usage_limits=UsageLimits(request_limit=MAX_REQUESTS_SYNTHESIS)
                        )
                        logger.info("✓ Created workspace files using agent history")
                    except Exception as retry_error:
                        logger.warning(f"Retry also failed: {str(retry_error)}")
                        logger.warning("Creating minimal workspace files as final fallback...")
                        try:
                            pom_path = os.path.join(java_output_path, "pom.xml")
                            with open(pom_path, 'w') as f:
                                f.write(f"""<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>translated</groupId>
  <artifactId>{repo_name}</artifactId>
  <version>1.0-SNAPSHOT</version>
  <packaging>pom</packaging>
  <modules>
{module_list_xml}
  </modules>
</project>
""")
                            readme_path = os.path.join(java_output_path, "README.md")
                            with open(readme_path, 'w') as f:
                                f.write(f"""# {repo_name}

Java translation of {repo_name} C repository.

## Modules

{chr(10).join(f'- `{k}`' for k in module_names)}

## Build

```bash
mvn test
```
""")
                            gitignore_path = os.path.join(java_output_path, ".gitignore")
                            with open(gitignore_path, 'w') as f:
                                f.write("target/\n")
                            logger.info("✓ Created minimal workspace files manually")
                        except Exception as fallback_error:
                            logger.error(f"Failed to create fallback files: {str(fallback_error)}")
            else:
                raise
        
        total_time = time.time() - translation_start
        
        logger.info("\n" + "="*80)
        logger.info("TRANSLATION WORKFLOW COMPLETED")
        logger.info("="*80)
        logger.info(f"Repository: {repo_name}")
        logger.info(f"Output: {java_output_path}")
        logger.info(f"Features translated: {len(feature_results)}")
        logger.info(f"\nPhase timing:")
        logger.info(f"   Per-feature translation: {features_time:.2f}s")
        logger.info(f"   Workspace synthesis:     {synthesis_time:.2f}s")
        logger.info(f"   Total Stage 3 time:      {total_time:.2f}s")
        
        if all_timings:
            logger.info(f"\nFeature timing breakdown (top 5):")
            sorted_timings = sorted(all_timings, key=lambda x: x['time'], reverse=True)
            for idx, timing in enumerate(sorted_timings[:5], 1):
                logger.info(f"   {idx}. {timing['feature']}: {timing['time']:.2f}s")
            if len(sorted_timings) > 5:
                logger.info(f"   ... and {len(sorted_timings) - 5} more features")
        
        logger.info("="*80 + "\n")
        
        return deps
