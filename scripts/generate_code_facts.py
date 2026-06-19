
"""
generate_code_facts.py

AST-based code facts extractor for multi-AI orchestration.
Emits a markdown report that feeds into initial_build_spec generation.

Usage:
    PYTHONPATH=src python scripts/generate_code_facts.py src/ > code_facts_report.md
"""

import ast
import sys
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class FunctionFact:
    name: str
    line: int
    signature: str
    docstring: str | None
    raises: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    http: bool = False
    env_vars: list[str] = field(default_factory=list)
    sys_path: bool = False
    is_async: bool = False
    decorators: list[str] = field(default_factory=list)


@dataclass
class ClassFact:
    name: str
    line: int
    bases: list[str]
    methods: list[FunctionFact] = field(default_factory=list)
    docstring: str | None = None


@dataclass
class ImportFact:
    source: str
    names: list[str]
    line: int
    is_from: bool = True
    is_runtime: bool = False  # sys.path.insert patterns


@dataclass
class ModuleFact:
    path: Path
    has_init: bool = False
    imports: list[ImportFact] = field(default_factory=list)
    functions: list[FunctionFact] = field(default_factory=list)
    classes: list[ClassFact] = field(default_factory=list)
    top_level_calls: list[str] = field(default_factory=list)
    env_vars: list[tuple[str, int]] = field(default_factory=list)
    sys_path_inserts: list[tuple[str, int]] = field(default_factory=list)


class CodeFactsExtractor(ast.NodeVisitor):
    HTTP_LIBRARIES = {"requests", "httpx", "urllib", "http.client", "aiohttp"}
    ENV_PATTERNS = {"os.environ", "os.getenv", "os.environ.get", "getenv"}
    RETRY_KEYWORDS = {"retry", "backoff", "sleep", "timeout", "rate_limit", "429"}

    def __init__(self, module_path: Path, project_root: Path):
        self.module_path = module_path
        self.project_root = project_root
        self.module = ModuleFact(path=module_path.relative_to(project_root))
        self._current_function: FunctionFact | None = None
        self._current_class: ClassFact | None = None
        self._imports: dict[str, str] = {}  # alias -> full name

    def analyze(self, source: str) -> ModuleFact:
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            self.module.functions.append(
                FunctionFact(
                    name="<parse_error>",
                    line=e.lineno or 0,
                    signature="",
                    docstring=str(e),
                )
            )
            return self.module

        self.visit(tree)
        return self.module

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            name = alias.asname or alias.name
            self._imports[name] = alias.name
            self.module.imports.append(
                ImportFact(
                    source=alias.name,
                    names=[alias.name],
                    line=node.lineno,
                    is_from=False,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        names = [a.name for a in node.names]
        for alias in node.names:
            local = alias.asname or alias.name
            self._imports[local] = f"{module}.{alias.name}" if module else alias.name

        self.module.imports.append(
            ImportFact(
                source=module,
                names=names,
                line=node.lineno,
                is_from=True,
            )
        )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Detect sys.path.insert
        if self._is_sys_path_insert(node):
            self.module.sys_path_inserts.append(
                (ast.unparse(node), node.lineno)
            )
            if self._current_function:
                self._current_function.sys_path = True

        # Detect HTTP calls
        if self._is_http_call(node):
            if self._current_function:
                self._current_function.http = True

        # Detect env access
        env_var = self._extract_env_var(node)
        if env_var:
            self.module.env_vars.append((env_var, node.lineno))
            if self._current_function:
                self._current_function.env_vars.append(env_var)

        # Detect function calls within functions
        if self._current_function:
            call_name = self._resolve_call_name(node)
            if call_name:
                self._current_function.calls.append(call_name)

        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        # Detect os.environ["KEY"] direct subscript access
        if (
            isinstance(node.value, ast.Attribute)
            and node.value.attr == "environ"
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "os"
        ):
            key_node = node.slice
            if isinstance(key_node, ast.Index):  # Python 3.8 compat
                key_node = key_node.value  # type: ignore[attr-defined]
            if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                env_var = key_node.value
                self.module.env_vars.append((env_var, node.lineno))
                if self._current_function:
                    self._current_function.env_vars.append(env_var)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        is_async = isinstance(node, ast.AsyncFunctionDef)
        sig = self._build_signature(node)
        doc = ast.get_docstring(node)

        func = FunctionFact(
            name=node.name,
            line=node.lineno,
            signature=sig,
            docstring=doc,
            is_async=is_async,
            decorators=[ast.unparse(d) for d in node.decorator_list],
        )

        # Detect raises
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if child.exc and isinstance(child.exc, ast.Call):
                    func.raises.append(self._resolve_name(child.exc.func))
                elif child.exc and isinstance(child.exc, ast.Name):
                    func.raises.append(child.exc.id)

        old_func = self._current_function
        self._current_function = func
        if self._current_class:
            self._current_class.methods.append(func)
        else:
            self.module.functions.append(func)

        self.generic_visit(node)
        self._current_function = old_func

    # Route async functions through the same handler
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef):
        bases = [self._resolve_name(b) for b in node.bases]
        cls = ClassFact(
            name=node.name,
            line=node.lineno,
            bases=bases,
            docstring=ast.get_docstring(node),
        )
        old_cls = self._current_class
        self._current_class = cls
        self.module.classes.append(cls)
        self.generic_visit(node)
        self._current_class = old_cls

    def _is_sys_path_insert(self, node: ast.Call) -> bool:
        try:
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "insert" and isinstance(node.func.value, ast.Attribute):
                    if node.func.value.attr == "path" and isinstance(node.func.value.value, ast.Name):
                        return node.func.value.value.id == "sys"
        except Exception:
            pass
        return False

    def _is_http_call(self, node: ast.Call) -> bool:
        # requests.post, httpx.get, etc.
        name = self._resolve_call_name(node)
        if not name:
            return False
        parts = name.split(".")
        return parts[0] in self.HTTP_LIBRARIES

    def _extract_env_var(self, node: ast.Call) -> str | None:
        # os.getenv("KEY"), os.environ.get("KEY"), os.environ["KEY"]
        name = self._resolve_call_name(node)
        if not name:
            return None

        if "os.environ" in name or "os.getenv" in name or "getenv" in name:
            # Try to extract the first string arg
            if node.args and isinstance(node.args[0], ast.Constant):
                return str(node.args[0].value)
            if node.args and isinstance(node.args[0], ast.Str):  # py<<3.8 compat
                return node.args[0].s
        return None

    def _resolve_call_name(self, node: ast.Call) -> str | None:
        if isinstance(node.func, ast.Name):
            return self._imports.get(node.func.id, node.func.id)
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current: ast.expr = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(self._imports.get(current.id, current.id))
            parts.reverse()
            return ".".join(parts)
        return None

    def _resolve_name(self, node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return self._imports.get(node.id, node.id)
        elif isinstance(node, ast.Attribute):
            return self._resolve_call_name(ast.Call(func=node, args=[], keywords=[])) or ast.unparse(node)
        return ast.unparse(node)

    def _build_signature(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        args = []
        for arg in node.args.posonlyargs:
            args.append(self._format_arg(arg))
        for arg in node.args.args:
            args.append(self._format_arg(arg))
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        for arg in node.args.kwonlyargs:
            args.append(self._format_arg(arg))
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        return f"{prefix} {node.name}({', '.join(args)})"

    def _format_arg(self, arg: ast.arg) -> str:
        if arg.annotation:
            return f"{arg.arg}: {ast.unparse(arg.annotation)}"
        return arg.arg


def discover_modules(root: Path) -> list[Path]:
    modules = []
    for py_file in sorted(root.rglob("*.py")):
        # Skip __pycache__ and venvs
        if "__pycache__" in str(py_file) or ".venv" in str(py_file):
            continue
        modules.append(py_file)
    return modules


def generate_report(project_root: Path, src_dirs: list[str]) -> str:
    lines = [
        "# Code Facts Report",
        f"Generated: {__import__('datetime').datetime.now().isoformat()}",
        f"Project Root: {project_root.resolve().name}/",
        f"PYTHONPATH Convention: {src_dirs[0].rstrip('/')}/",
        "",
        "---",
        "",
    ]

    all_modules: list[ModuleFact] = []
    src_paths = [project_root / d for d in src_dirs]

    # 1. Structure
    lines.append("## 1. Project Structure\n")
    lines.append("| Path | Type | Has __init__.py | Notes |")
    lines.append("|------|------|-----------------|-------|")

    SKIP = {"__pycache__", ".git", ".venv", "node_modules", ".pytest_cache"}

    for src in src_paths:
        for py_file in sorted(src.rglob("*")):
            if any(part in SKIP for part in py_file.parts):
                continue
            rel = py_file.relative_to(project_root)
            if py_file.is_dir():
                init = (py_file / "__init__.py").exists()
                status = "yes" if init else "**MISSING**"
                lines.append(f"| {rel}/ | package | {status} | |")
            elif py_file.is_file() and py_file.suffix == ".py":
                lines.append(f"| {rel} | module | n/a | |")

    # Analyze modules
    for src in src_paths:
        for py_file in sorted(src.rglob("*.py")):
            if any(part in SKIP for part in py_file.parts):
                continue
            try:
                source = py_file.read_text(encoding="utf-8")
            except Exception:
                continue
            extractor = CodeFactsExtractor(py_file, project_root)
            mod = extractor.analyze(source)
            all_modules.append(mod)

    # 2. Import Graph
    lines.extend(["", "## 2. Import Graph (Cross-Module)\n"])
    lines.append("| Source Module | Imports From | Imported Names | Line |")
    lines.append("|---------------|--------------|----------------|------|")
    for mod in all_modules:
        for imp in mod.imports:
            if imp.is_runtime:
                continue
            src = str(mod.path)
            lines.append(f"| {src} | {imp.source} | {', '.join(imp.names)} | {imp.line} |")

    # 3. Function Signatures — top-level functions and class methods
    lines.extend(["", "## 3. Function Signatures (Transport & Domain Boundaries)\n"])
    for mod in all_modules:
        all_funcs: list[tuple[FunctionFact, str | None]] = [(f, None) for f in mod.functions]
        for cls in mod.classes:
            all_funcs.extend((m, cls.name) for m in cls.methods)
        for func, class_name in all_funcs:
            qualifier = f"{class_name}.{func.name}" if class_name else func.name
            lines.append(f"### {mod.path}::{qualifier}")
            lines.append("```python")
            lines.append(func.signature)
            lines.append(f"    # Line: {func.line}")
            if func.is_async:
                lines.append("    # Async: Yes")
            if func.docstring:
                lines.append(f"    # Docstring: {func.docstring[:100]}...")
            if func.raises:
                lines.append(f"    # Raises: {', '.join(func.raises)}")
            if func.http:
                lines.append("    # HTTP: Yes — requests/httpx call inside")
            if func.env_vars:
                lines.append(f"    # Env vars: {', '.join(func.env_vars)}")
            if func.sys_path:
                lines.append("    # sys.path: Runtime path manipulation detected")
            if func.calls:
                lines.append(f"    # Calls: {', '.join(func.calls[:5])}")
            lines.append("```\n")

    # 4. Class Hierarchies
    lines.extend(["", "## 4. Class Hierarchies\n"])
    for mod in all_modules:
        for cls in mod.classes:
            lines.append(f"### {cls.name}")
            lines.append(f"- File: {mod.path}")
            lines.append(f"- Line: {cls.line}")
            lines.append(f"- Bases: {', '.join(cls.bases) if cls.bases else 'object'}")
            for method in cls.methods:
                async_tag = " (async)" if method.is_async else ""
                lines.append(f"  - {method.name}(){async_tag} — line {method.line}")
            lines.append("")

    # 5. Transport/HTTP Call Sites — confirmed calls only, no name-based guessing
    lines.extend(["", "## 5. Transport/HTTP Call Sites\n"])
    lines.append("| File | Class | Function | Line | Env Vars |")
    lines.append("|------|-------|----------|------|----------|")
    for mod in all_modules:
        all_funcs_http: list[tuple[FunctionFact, str | None]] = [(f, None) for f in mod.functions]
        for cls in mod.classes:
            all_funcs_http.extend((m, cls.name) for m in cls.methods)
        for func, class_name in all_funcs_http:
            if func.http:
                lines.append(
                    f"| {mod.path} | {class_name or '-'} | {func.name} | {func.line} | "
                    f"{', '.join(func.env_vars) if func.env_vars else '-'} |"
                )

    # 6. sys.path hacks
    lines.extend(["", "## 6. sys.path.insert & Runtime Path Hacks\n"])
    lines.append("| File | Lines | Code |")
    lines.append("|------|-------|------|")
    for mod in all_modules:
        for code, lineno in mod.sys_path_inserts:
            lines.append(f"| {mod.path} | {lineno} | `{code[:80]}` |")

    # 7. Env vars
    lines.extend(["", "## 7. Env Access Patterns\n"])
    lines.append("| File | Env Var | Line |")
    lines.append("|------|---------|------|")
    for mod in all_modules:
        for var, lineno in mod.env_vars:
            lines.append(f"| {mod.path} | {var} | {lineno} |")

    # 8. Test Inventory
    lines.extend(["", "## 8. Test Inventory\n"])
    lines.append("| Test File | Target | Notes |")
    lines.append("|-----------|--------|-------|")
    for mod in all_modules:
        if "test" in str(mod.path).lower():
            lines.append(f"| {mod.path} | — | |")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_code_facts.py <src_dir> [src_dir2 ...]")
        sys.exit(1)

    root = Path(".")
    srcs = sys.argv[1:]
    print(generate_report(root, srcs))