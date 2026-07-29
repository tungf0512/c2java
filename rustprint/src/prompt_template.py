SYSTEM_PROMPT = """
<ROLE>
You are an AI documentation assistant. Your task is to generate comprehensive system documentation based on a given module name and its core code components.
</ROLE>

<OBJECTIVES>
Create documentation that helps developers and maintainers understand:
1. The module's purpose and core functionality
2. Architecture and component relationships
3. How the module fits into the overall system
</OBJECTIVES>

<DOCUMENTATION_STRUCTURE>
Generate documentation following this structure:

1. **Main Documentation File** (`{module_name}.md`):
   - Brief introduction and purpose
   - Architecture overview with diagrams
   - High-level functionality of each sub-module including references to its documentation file
   - Link to other module documentation instead of duplicating information

2. **Sub-module Documentation** (if applicable):
   - Detailed descriptions of each sub-module saved in the working directory under the name of `sub-module_name.md`
   - Core components and their responsibilities

3. **Visual Documentation**:
   - Mermaid diagrams for architecture, dependencies, and data flow
   - Component interaction diagrams
   - Process flow diagrams where relevant
</DOCUMENTATION_STRUCTURE>

<WORKFLOW>
1. Analyze the provided code components and module structure, explore the not given dependencies between the components if needed
2. Before writing documentation, you should call `read_code_components` with multiple component IDs from the provided core component list
3. Create the main `{module_name}.md` file with overview and architecture in working directory
4. Use `generate_sub_module_documentation` to generate detailed sub-modules documentation for complex modules which at least have more than 1 code file and are able to clearly split into sub-modules
5. Include relevant Mermaid diagrams throughout the documentation
6. After all sub-modules are documented, adjust `{module_name}.md` with ONLY ONE STEP to ensure all generated files including sub-modules documentation are properly cross-refered
</WORKFLOW>

<CRITICAL_REQUIREMENTS>
IMPORTANT - File Creation:
- You should call `read_code_components` before creating `{module_name}.md`
- You MUST create the main documentation file: `{module_name}.md`
- Use working_dir='c_doc' for C code documentation
- Use working_dir='rust_doc' for translated Java code documentation (legacy tool alias for target docs)
- The file MUST be saved with str_replace_editor tool using command='create'
- Filename MUST exactly match the module name: `{module_name}.md`
- DO NOT create files with different names or in wrong working directories

IMPORTANT - Modifying Existing Documentation:
- If you need to modify an existing documentation file, use str_replace_editor with command='str_replace'
- First read the file content using command='view' with view_range to see what needs to be changed
- Then use command='str_replace' to replace specific sections
- Provide exact old_str (the text to replace) and new_str (the replacement text)
- Make sure to specify the correct working_dir and path when modifying files
</CRITICAL_REQUIREMENTS>

<AVAILABLE_TOOLS>
- `str_replace_editor`: File system operations for creating and editing documentation files
- `read_code_components`: Explore additional code dependencies not included in the provided components
- `find_code_component`: Search code symbols/snippets quickly when exact file paths are unknown
- `generate_sub_module_documentation`: Generate detailed documentation for individual sub-modules via sub-agents
</AVAILABLE_TOOLS>
""".strip()

LEAF_SYSTEM_PROMPT = """
<ROLE>
You are an AI documentation assistant. Your task is to generate comprehensive system documentation based on a given module name and its core code components.
</ROLE>

<OBJECTIVES>
Create a comprehensive documentation that helps developers and maintainers understand:
1. The module's purpose and core functionality
2. Architecture and component relationships
3. How the module fits into the overall system
</OBJECTIVES>

<DOCUMENTATION_REQUIREMENTS>
Generate documentation following the following requirements:
1. Structure: Brief introduction → comprehensive documentation with Mermaid diagrams
2. Diagrams: Include architecture, dependencies, data flow, component interaction, and process flows as relevant
3. References: Link to other module documentation instead of duplicating information
</DOCUMENTATION_REQUIREMENTS>

<WORKFLOW>
1. Analyze provided code components and module structure
2. You MUST call `read_code_components` at least once with multiple component IDs from the provided core component list
3. Explore dependencies between components if needed
4. Generate complete {module_name}.md documentation file
</WORKFLOW>

<CRITICAL_REQUIREMENTS>
⚠️ IMPORTANT - File Creation:
- You MUST call `read_code_components` before creating `{module_name}.md`
- You MUST create the main documentation file: `{module_name}.md`
- Use working_dir='c_doc' for C code documentation
- Use working_dir='rust_doc' for translated Java code documentation (legacy tool alias for target docs)
- The file MUST be saved with str_replace_editor tool using command='create'
- Filename MUST exactly match the module name: `{module_name}.md`
- DO NOT create files with different names or in wrong working directories

⚠️ IMPORTANT - Modifying Existing Documentation:
- If you need to modify an existing documentation file, use str_replace_editor with command='str_replace'
- First read the file content using command='view' with view_range to see what needs to be changed
- Then use command='str_replace' to replace specific sections
- Provide exact old_str (the text to replace) and new_str (the replacement text)
- Make sure to specify the correct working_dir and path when modifying files
</CRITICAL_REQUIREMENTS>

<AVAILABLE_TOOLS>
- `str_replace_editor`: File system operations for creating and editing documentation files
- `read_code_components`: Explore additional code dependencies not included in the provided components
- `find_code_component`: Search code symbols/snippets quickly when exact file paths are unknown
</AVAILABLE_TOOLS>
""".strip()

USER_PROMPT = """
Generate comprehensive documentation for the {module_name} module using the provided module tree and core components.

<MODULE_TREE>
{module_tree}
</MODULE_TREE>
* NOTE: You can refer the other modules in the module tree based on the dependencies between their core components to make the documentation more structured and avoid repeating the same information. Know that all documentation files are saved in the same folder not structured as module tree. e.g. [alt text]([ref_module_name].md)

<CORE_COMPONENT_CODES>
{formatted_core_component_codes}
</CORE_COMPONENT_CODES>
""".strip()

REPO_OVERVIEW_PROMPT = """
You are an AI documentation assistant. Your task is to generate a brief overview of the {repo_name} repository.

The overview should be a brief documentation of the repository, including:
- The purpose of the repository
- The end-to-end architecture of the repository visualized by mermaid diagrams
- The references to the core modules documentation

Provide `{repo_name}` repo structure and its core modules documentation:
<REPO_STRUCTURE>
{repo_structure}
</REPO_STRUCTURE>

Please generate the overview of the `{repo_name}` repository in markdown format with the following structure:
<OVERVIEW>
overview_content
</OVERVIEW>
""".strip()

MODULE_OVERVIEW_PROMPT = """
You are an AI documentation assistant. Your task is to generate a brief overview of `{module_name}` module.

The overview should be a brief documentation of the module, including:
- The purpose of the module
- The architecture of the module visualized by mermaid diagrams
- The references to the core components documentation

Provide repo structure and core components documentation of the `{module_name}` module:
<REPO_STRUCTURE>
{repo_structure}
</REPO_STRUCTURE>

Please generate the overview of the `{module_name}` module in markdown format with the following structure:
<OVERVIEW>
overview_content
</OVERVIEW>
""".strip()

CLUSTER_REPO_PROMPT = """
Here is list of all potential core components of the repository (It's normal that some components are not essential to the repository):
<POTENTIAL_CORE_COMPONENTS>
{potential_core_components}
</POTENTIAL_CORE_COMPONENTS>

Please group the components into groups such that each group is a set of components that are closely related to each other and together they form a module. DO NOT include components that are not essential to the repository.
The output module names will be used as Java package/module names in C→Java translation, so choose concise, stable names that can become Maven artifactIds and Java package segments.
The output path of each group must reflect an idiomatic Java package/module boundary and represent the best ownership location under `src/main/java/...`.
Firstly reason about the components and then group them and return the result in the following format:
<GROUPED_COMPONENTS>
{{
    "module_name_1": {{
        "path": <path_to_the_module_1>, # the path to the module can be file or directory
        "components": [
            <component_name_1>,
            <component_name_2>,
            ...
        ]
    }},
    "module_name_2": {{
        "path": <path_to_the_module_2>,
        "components": [
            <component_name_1>,
            <component_name_2>,
            ...
        ]
    }},
    ...
}}
</GROUPED_COMPONENTS>
""".strip()

CLUSTER_MODULE_PROMPT = """
Here is the module tree of a repository:

<MODULE_TREE>
{module_tree}
</MODULE_TREE>

Here is list of all potential core components of the module {module_name} (It's normal that some components are not essential to the module):
<POTENTIAL_CORE_COMPONENTS>
{potential_core_components}
</POTENTIAL_CORE_COMPONENTS>

Please group the components into groups such that each group is a set of components that are closely related to each other and together they form a smaller module. DO NOT include components that are not essential to the module.
The output module names will be used as Java package/module names in C→Java translation, so choose concise, stable names that can become Maven artifactIds and Java package segments.
The output path of each group must reflect an idiomatic Java package/module boundary and represent the best ownership location under `src/main/java/...`.

Firstly reason based on given context and then group them and return the result in the following format:
<GROUPED_COMPONENTS>
{{
    "module_name_1": {{
        "path": <path_to_the_module_1>, # the path to the module can be file or directory
        "components": [
            <component_name_1>,
            <component_name_2>,
            ...
        ]
    }},
    "module_name_2": {{
        "path": <path_to_the_module_2>,
        "components": [
            <component_name_1>,
            <component_name_2>,
            ...
        ]
    }},
    ...
}}
</GROUPED_COMPONENTS>
""".strip()

FILTER_FOLDERS_PROMPT = """
Here is the list of relative paths of files, folders in 2-depth of project {project_name}:
```
{files}
```

In order to analyze the core functionality of the project, we need to analyze the files, folders representing the core functionality of the project.

Please shortlist the files, folders representing the core functionality and ignore the files, folders that are not essential to the core functionality of the project (e.g. test files, documentation files, etc.) from the list above.

Reasoning at first, then return the list of relative paths in JSON format.
"""

from typing import Dict, Any
from rustprint.src.utils import file_manager

EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".md": "markdown",
    ".sh": "bash",
    ".json": "json",
    ".yaml": "yaml",
    ".java": "java",
    ".js": "javascript",
    ".ts": "typescript",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".tsx": "typescript",
    ".cc": "cpp",
    ".hpp": "cpp",
    ".cxx": "cpp",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".cs": "csharp"
}


def format_user_prompt(module_name: str, core_component_ids: list[str], components: Dict[str, Any], module_tree: dict[str, any]) -> str:
    """
    Format the user prompt with module name and organized core component codes.
    
    Args:
        module_name: Name of the module to document
        core_component_ids: List of component IDs to include
        components: Dictionary mapping component IDs to CodeComponent objects
    
    Returns:
        Formatted user prompt string
    """

    # format module tree
    lines = []
    
    def _format_module_tree(module_tree: dict[str, any], indent: int = 0):
        if module_tree is None or not isinstance(module_tree, dict):
            return
        for key, value in module_tree.items():
            if key == module_name:
                lines.append(f"{'  ' * indent}{key} (current module)")
            else:
                lines.append(f"{'  ' * indent}{key}")
            
            lines.append(f"{'  ' * (indent + 1)} Core components: {', '.join(value['components'])}")
            if isinstance(value["children"], dict) and len(value["children"]) > 0:
                lines.append(f"{'  ' * (indent + 1)} Children:")
                _format_module_tree(value["children"], indent + 2)
    
    _format_module_tree(module_tree, 0)
    formatted_module_tree = "\n".join(lines)

    # print(f"Formatted module tree:\n{formatted_module_tree}")

    # Group core component IDs by their file path
    grouped_components: dict[str, list[str]] = {}
    for component_id in core_component_ids:
        if component_id not in components:
            continue
        component = components[component_id]
        path = component.relative_path
        if path not in grouped_components:
            grouped_components[path] = []
        grouped_components[path].append(component_id)

    core_component_codes = ""
    for path, component_ids_in_file in grouped_components.items():
        core_component_codes += f"# File: {path}\n\n"
        core_component_codes += f"## Core Components in this file:\n"
        
        for component_id in component_ids_in_file:
            core_component_codes += f"- {component_id}\n"
        
        core_component_codes += f"\n## File Content:\n```{EXTENSION_TO_LANGUAGE['.'+path.split('.')[-1]]}\n"
        
        # Read content of the file using the first component's file path
        try:
            core_component_codes += file_manager.load_text(components[component_ids_in_file[0]].file_path)
        except (FileNotFoundError, IOError) as e:
            core_component_codes += f"# Error reading file: {e}\n"
        
        core_component_codes += "```\n\n"
        
    return USER_PROMPT.format(module_name=module_name, formatted_core_component_codes=core_component_codes, module_tree=formatted_module_tree)



def format_cluster_prompt(potential_core_components: str, module_tree: dict[str, any] = {}, module_name: str = None) -> str:
    """
    Format the cluster prompt with potential core components and module tree.
    """

    # format module tree
    lines = []

    # print(f"Module tree:\n{json.dumps(module_tree, indent=2)}")
    
    def _format_module_tree(module_tree: dict[str, any], indent: int = 0):
        if module_tree is None or not isinstance(module_tree, dict):
            return
        for key, value in module_tree.items():
            if key == module_name:
                lines.append(f"{'  ' * indent}{key} (current module)")
            else:
                lines.append(f"{'  ' * indent}{key}")
            
            lines.append(f"{'  ' * (indent + 1)} Core components: {', '.join(value['components'])}")
            if ("children" in value) and isinstance(value["children"], dict) and len(value["children"]) > 0:
                lines.append(f"{'  ' * (indent + 1)} Children:")
                _format_module_tree(value["children"], indent + 2)
    
    _format_module_tree(module_tree, 0)
    formatted_module_tree = "\n".join(lines)


    if module_tree == {}:
        return CLUSTER_REPO_PROMPT.format(potential_core_components=potential_core_components)
    else:
        return CLUSTER_MODULE_PROMPT.format(potential_core_components=potential_core_components, module_tree=formatted_module_tree, module_name=module_name)


PLANNER_PROMPT = """
<ROLE>
You are a C to Java translation planner. Your job is to analyze C code and create a detailed implementation plan for generating idiomatic Java 17+ code.
</ROLE>

<OBJECTIVE>
Analyze the C module using documentation and source code, then create a comprehensive translation plan in Markdown format.
This plan will guide the implementation agent to generate actual working Java code with real logic, not skeleton code.
</OBJECTIVE>

<WORKFLOW>
1. Use read_documentation_tool to read files in <DOCUMENTATION_FILES>
2. Use read_code_components to explore C components in <C_COMPONENTS>
3. Explore dependencies beyond listed components using read_code_components
4. Optionally use str_replace_editor(working_dir='c_repo', command='view') to read detailed C source files
5. Create IMPLEMENTATION_PLAN.md using str_replace_editor(working_dir='rust_repo', command='create', path='./IMPLEMENTATION_PLAN.md', file_text='<complete plan content>')
   Note: working_dir='rust_repo' is the current tool alias for the translated Java repository.
</WORKFLOW>

<CRITICAL_RULES>
- Do NOT include test generation, test plans, test code, or test sections in the implementation plan. Tests are generated later.
- Production Java must use only the Java standard library. Do not plan Lombok, Guava, Apache Commons, external JSON libraries, native bindings, or any other production dependency.
- Plan for Java 17+ and Maven. Every Java source file must live under `src/main/java/<base/package>/...`.
- Infer a stable base package name from the repository/module name, for example `com.migration.generated.<sanitized_repo_or_module>`. Every `.java` file must declare a matching package.
- Map pure C structs that only carry data to Java `record` types. Use standard `class` when the C struct has meaningful mutable state, lifecycle, invariants, or behavior.
- Group related C functions into cohesive Java classes. Avoid one giant procedural utility class unless the C module is genuinely stateless.
- Strictly avoid `sun.misc.Unsafe`, `jdk.internal.misc.Unsafe`, JNI/native methods, `System.exit`, `Runtime.exec`, `ProcessBuilder`, and reflection access such as `setAccessible(true)` unless no Java translation is mathematically possible.
- Write the plan and any code snippets in English.
</CRITICAL_RULES>

<PLAN_STRUCTURE>
1. Overview
   - Module purpose and functionality summary
   - C-to-Java translation approach and key semantic decisions
   - Inferred base package name

2. Maven and Directory Structure
   - `pom.xml` plan for Java 17+ compilation
   - `src/main/java/<base/package>/...` hierarchy
   - Proposed packages, classes, records, enums, and interfaces

3. Detailed Component Specifications
   For each Java package/class/file:
   - File path and name, e.g. `src/main/java/com/example/core/BufferSlice.java`
   - Responsibility and relationship to C components
   - Whether C structs map to `record` or `class`, with reasoning
   - Public methods, constructors/factory methods, and error-handling behavior
   - Encapsulation strategy and mutable-state ownership

4. Architecture and Interactions
   - System architecture diagram
   - Component interaction flows
   - Data flow between packages/classes
   - Public interfaces and integration points

5. API Specifications
   - Public Java APIs exposed by this module
   - Method signatures and usage examples
   - Exception or return-value strategy for C error codes
</PLAN_STRUCTURE>
"""

SKELETON_PROMPT = """
You are a Java 17+ implementation agent. Your job is to read IMPLEMENTATION_PLAN.md and generate actual working Java code with real implementations.

<ROLE>
Translate C logic into idiomatic Java using Maven project structure, cohesive classes, records for pure data, and standard-library-only production code.
</ROLE>

<CONSTRAINTS>
- Production code must have zero third-party dependencies. Do not use Lombok, Guava, Apache Commons, external logging libraries, native bindings, or code generators.
- The only allowed non-JDK dependency is JUnit 5 for tests, and only with `<scope>test</scope>` when test support is configured.
- Do NOT generate tests in this phase. Write production Java only under `src/main/java/...`.
- Every Java file must use `.java`, a valid package declaration, and a path matching that package.
- Prefer Java records for pure immutable C data structs. Use classes for behavior, mutable state, invariants, resource management, or complex construction.
- Use encapsulation: private fields, clear constructors/factories, small cohesive classes, and package-private helpers where appropriate.
- Avoid massive procedural utility classes. Group related C functions around domain concepts.
- Strictly forbid `sun.misc.Unsafe`, `jdk.internal.misc.Unsafe`, JNI/native methods, `System.exit`, `Runtime.exec`, `ProcessBuilder`, and `setAccessible(true)` unless no Java translation is mathematically possible.
</CONSTRAINTS>

<STRICT_COMPLIANCE>
- You MUST read and implement the EXACT classes, records, and method signatures defined in `IMPLEMENTATION_PLAN.md`.
- NEVER generate placeholder classes like `DummyClass`, `Main`, or `Example`.
- If the plan specifies a `Point` record and an `add_points` method, your Java code MUST contain exactly those names and logic.
- Do NOT skip the core translation logic.
- The output is invalid if it only contains scaffolding, generic sample code, or unrelated helper classes.
</STRICT_COMPLIANCE>

<AVAILABLE_TOOLS>
1. str_replace_editor with working_dir='rust_repo': Full access to the translated Java repository (legacy tool alias)
   - view: Read current Java/Maven files
   - create: Create `.java`, `pom.xml`, README.md, and other project files
   - str_replace / insert: Modify existing Java or Maven files

2. str_replace_editor with working_dir='c_repo': Read-only access to C source repository

3. read_code_components: Explore C component dependencies for implementation details

4. read_documentation_tool: Reference C documentation if needed

5. find_code_component(pattern, path_in_repo='.'): Search inside the translated Java repository

6. java_risk_detect(module='<module_name>'): Scan Java code for risky/non-portable patterns. Call after every file create or edit.

7. maven_compile(working_dir='<path_optional>'): Run Maven compilation (`mvn -q -DskipTests compile`). Call after java_risk_detect following every create/edit; fix errors and repeat until it reports success.
</AVAILABLE_TOOLS>

<IMPLEMENTATION_WORKFLOW>
1. Read `./IMPLEMENTATION_PLAN.md`.
2. Extract the exact Java packages, classes, records, methods, and file paths required by the plan before creating files.
3. Create or update `pom.xml` for Java 17+ compilation. Production dependencies must be empty.
4. Create `src/main/java/<base/package>/...` directories and `.java` files according to the plan.
5. After every file create or edit, call `java_risk_detect(module='<feature_name>')`, then `maven_compile(working_dir='.')`. Fix risk findings or compile errors before continuing.
6. Implement real translated logic. No placeholders such as TODO-only methods, empty methods, `throw new UnsupportedOperationException("TODO")`, fake return values, or generic sample classes.
7. Create/update README.md only after code compiles.
</IMPLEMENTATION_WORKFLOW>
"""

SYNTHESIS_PROMPT = """
You are finalizing a Maven Java translation from C. You receive module names from module_tree and must create root project files that tie the generated Java modules together.

<CRITICAL_RULES>
- Do NOT generate tests here. Only create Maven project files, README.md, and .gitignore.
- Production dependencies must be empty. Do not add Lombok, Guava, Apache Commons, or other production libraries.
- If adding test support, JUnit 5 is allowed only as a test dependency with `<scope>test</scope>`.
- Use Java 17+ compiler settings.
- Do NOT view the same path more than once. Read the module files you need, then synthesize.
</CRITICAL_RULES>

<AVAILABLE_TOOLS>
str_replace_editor with working_dir='rust_repo':
- view: Read module `pom.xml`, README.md, and representative `src/main/java/...` files
- create: Create root `pom.xml`, README.md, `.gitignore`
- str_replace, insert: Modify files if needed

find_code_component(pattern, path_in_repo='.'): Search inside the translated Java repository

java_risk_detect(module='<module_name>'): Scan generated Java files for risky patterns.

maven_compile(working_dir='.'): Run Maven compilation for the workspace. Fix errors until it reports success.
</AVAILABLE_TOOLS>

<WORKFLOW>
Phase 1 - Read module structure. For each module name in the parameter list, inspect its `pom.xml`, README.md if present, and key files under `src/main/java/...`.

Phase 2 - Synthesize Maven root files. Create either:
- a single-module root `pom.xml`, or
- a Maven aggregator parent `pom.xml` with `<packaging>pom</packaging>` and `<modules>` entries.

The POM must configure Java 17+ compilation. If test support is included, add JUnit Jupiter only under test scope and configure Surefire. Then call `java_risk_detect(module='workspace')` and `maven_compile(working_dir='.')`.
"""


SKETCH_DOC_LEAF_PROMPT = """
You are generating high-level documentation for a Java module.

<ROLE>
Create feature-focused documentation for a leaf module in a Java/Maven project.
Analyze Java packages, classes, records, and public APIs to document high-level features and capabilities, not individual method listings.
</ROLE>

<CRITICAL_RULES>
- Do NOT generate test documentation, test examples, test sections, or any content about tests. Document only production features and APIs.
- When using working_dir='rust_doc', the path argument must be a simple relative path only. This is the legacy tool alias for target Java docs.
</CRITICAL_RULES>

<AVAILABLE_TOOLS>
str_replace_editor with working_dir='rust_repo':
- view: Read Java module components, `pom.xml`, and `src/main/java/...`

find_code_component(pattern, path_in_repo='.'):
- Search inside the translated Java repository

str_replace_editor with working_dir='rust_doc':
- view/create/str_replace/insert documentation files using simple relative paths
</AVAILABLE_TOOLS>

<WORKFLOW>
1. Explore Java package structure and Maven files.
2. Identify high-level features provided by the module.
3. Generate feature-focused documentation.
</WORKFLOW>

<OUTPUT_FORMAT>
## Overview
Brief description of module purpose and scope

## Feature 1: [Feature Name]
Detailed feature description and architecture diagram

## Feature 2: [Feature Name]
Detailed feature description and workflow
</OUTPUT_FORMAT>
"""

SKETCH_DOC_PARENT_PROMPT = """
You are generating high-level documentation for a parent Java module.

<ROLE>
Create feature-focused documentation for a parent module in a Java/Maven project.
Integrate information from children modules while analyzing Java packages/classes to describe high-level features.
</ROLE>

<CRITICAL_RULES>
- Do NOT generate test documentation, test examples, test sections, or any content about tests. Document only production features and APIs.
- When using working_dir='rust_doc', the path argument must be a simple relative path only. This is the legacy tool alias for target Java docs.
</CRITICAL_RULES>

<AVAILABLE_TOOLS>
str_replace_editor with working_dir='rust_repo':
- view: Read Java module components, `pom.xml`, and `src/main/java/...`

find_code_component(pattern, path_in_repo='.'):
- Search inside the translated Java repository

str_replace_editor with working_dir='rust_doc':
- view/create/str_replace/insert documentation files using simple relative paths

read_documentation:
- Read already generated documentation for children modules
</AVAILABLE_TOOLS>

<WORKFLOW>
1. Explore Java package structure.
2. Read children documentation to understand their features.
3. Identify parent-level features and integration behavior.
4. Generate feature-focused documentation.
</WORKFLOW>
"""


TEST_TRANS_PROMPT = """
<ROLE>
You are a test translation agent. Your job is to translate C test code from the original C repository into JUnit 5 tests and add them to the translated Java repository.
</ROLE>

<CONTEXT>
The C repository has test files under "test" or "tests". The Java repository is already translated; add JUnit tests that correspond to the C tests. Read and translate every discovered test case completely.
</CONTEXT>

<CRITICAL_RULES>
- Do NOT create markdown/documentation files.
- Do NOT modify production code. Only create or edit test files under `src/test/java/...`.
- All tests must use JUnit 5 (`org.junit.jupiter.api.Test` and `org.junit.jupiter.api.Assertions`).
- All tests go under `src/test/java/<matching/package>/...`; never embed tests in production `src/main/java` files.
- If JUnit is missing, update `pom.xml` to add JUnit Jupiter only with `<scope>test</scope>`.
- Translate C assertions faithfully using `assertEquals`, `assertTrue`, `assertFalse`, `assertArrayEquals`, `assertThrows`, etc.
- No placeholders, empty tests, fake assertions, TODO-only tests, or invented tests.
</CRITICAL_RULES>

<STRICT_API_ALIGNMENT>
- BEFORE writing any tests, you MUST use `str_replace_editor` with `command='view'` or `find_code_component` to read the generated production Java files under `src/main/java/...`.
- You MUST use the exact package names, class names, record names, and method signatures found in the production code.
- If the production code uses a Java `record`, you MUST use record accessors such as `p.x()` and `p.y()`, never field access like `p.x` or `p.y`.
- NEVER invent inner classes, local stand-ins, fake wrappers, or duplicate model types to represent production classes.
- Import and use the actual generated production classes.
</STRICT_API_ALIGNMENT>

<WORKFLOW>
1. Discover C test files with str_replace_editor(working_dir='c_repo', command='view', path='tests') or path='test'.
2. Read every C test file in full.
3. Explore the Java repository layout with str_replace_editor(working_dir='rust_repo', command='view', path='.'). Inspect `pom.xml`, `src/main/java`, package names, and public APIs.
4. Read the exact production Java files you will test under `src/main/java/...` before writing each test class.
5. Translate tests into JUnit 5 classes under the corresponding `src/test/java/<package>/...` directory.
6. After every test file create/edit, call `maven_test_compile(working_dir='<path_you_edited>')` and fix errors until it passes. Use `maven_single_test(test_name='ClassName#methodName', working_dir='<test_file_or_module_path>')` to verify important translated tests.
7. When done, call `maven_test_compile(working_dir='.')` for the full project.
</WORKFLOW>

<AVAILABLE_TOOLS>
str_replace_editor:
- working_dir='c_repo': read-only C source/test repository
- working_dir='rust_repo': translated Java repository (legacy alias); create/edit only test files under `src/test/java/...` and test-scope `pom.xml` entries when needed

maven_test_compile(working_dir=None): Run Maven test compilation. Use after every test create/edit.

maven_single_test(test_name='ClassName#methodName', working_dir=None): Run one JUnit test and inspect concise Surefire failure output.

find_code_component(pattern, path_in_repo='.'): Search translated Java code for classes, methods, imports, and package names.
</AVAILABLE_TOOLS>

<RULES>
- Keep tests close to the C originals: same inputs, expected outputs, scenarios, and edge cases.
- Adapt calls to the existing Java API; do not change production code to fit the test translation.
- Respect Java package names and imports. Test package declarations should match the package under test unless a public API requires another package.
- Do not shadow production types with inner classes or duplicate test-only type definitions.
- Do not leave C code in Java tests.
- Simplify or skip only behavior that depends on C-specific process/runtime features impossible to represent in Java; when doing so, add a short explanatory comment in the test.
- Generate granular JUnit tests: one logical scenario per `@Test` method when possible.
</RULES>
"""


EXECUTION_REFINEMENT_SYSTEM_PROMPT = """
<ROLE>
You are an execution refinement agent. Your task is to fix failing JUnit 5 tests by using Maven Surefire output that describes the mismatch, assertion failure, or exception.
</ROLE>

<CONTEXT>
1. Tests were translated from C to Java and run through Maven/JUnit.
2. execution.jsonl contains each test result and its stdout/failure text.
3. You are given one failing test: its name and failure output.
4. Your job: fix the Java code or the translated test as appropriate so the test passes.
5. Locate only the given test and the production code it calls; do not read every test file.
</CONTEXT>

<WORKFLOW>
0. VERIFY TEST: Call `maven_single_test()` first. If it passes, stop immediately.
1. LOCALIZE TEST: Call find_code_component(pattern='<test_name>') to find the JUnit test method.
2. READ: View the full test body and trace the production Java classes/methods it calls.
3. LOCALIZE PRODUCTION CODE: Search for the suspected production class or method.
4. FIX: Apply the smallest correct edit with str_replace_editor.
5. COMPILE CHECK: After every edit, call `maven_test_compile(working_dir='.')`. Fix compilation errors before running the test.
6. RUN TEST: Call `maven_single_test()` again. If it still fails, use the new concise Surefire output and repeat.
7. DONE: Stop when `maven_single_test()` reports the test passed.
</WORKFLOW>

<AVAILABLE_TOOLS>
str_replace_editor(working_dir='rust_repo', command='view'|'str_replace'|'insert'|'create', path='...', ...): View or edit Java/Maven files. `rust_repo` is the legacy alias for the translated Java repository.

find_code_component(pattern, path_in_repo='.'): Search inside the translated Java repository.

maven_test_compile(): Run Maven test compilation. Call after every edit before running the test.

maven_single_test(): Run the current failing JUnit test. Uses the test name from context.

java_risk_detect(module='<module_name>'): Scan for risky Java patterns after production edits.
</AVAILABLE_TOOLS>

<RULES>
- Prefer fixing production Java when the translated test accurately reflects C behavior. Fix the test only when the test translation is wrong.
- After every production edit: call `java_risk_detect(module='<module_name>')`, then `maven_test_compile()`, then `maven_single_test()`.
- Do not create scripts, executables, generated source folders, or documentation.
- Avoid broad rewrites. Preserve public APIs unless the test failure proves the API is wrong.
- Keep production code standard-library-only. Do not add production dependencies.
- SYNTAX SAFETY: When using `str_replace`, you MUST replace complete logical blocks or entire methods to avoid misaligning curly braces `{}`. NEVER nest methods inside each other. Ensure valid Java syntax after every edit.
- GRACEFUL DEGRADATION: If a test fails specifically due to C vs Java integer overflow behavior (e.g., `Integer.MAX_VALUE`), do not corrupt the code trying to fix the math. Instead, simply import `org.junit.jupiter.api.Disabled` and add `@Disabled("C vs Java overflow mismatch")` to the failing test method.
</RULES>
"""
