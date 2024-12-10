import ast
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import customtkinter as ctk
from database.manager import DatabaseManager

@dataclass
class ModuleOption:
    name: str
    description: str
    type: str
    default: Any
    required: bool = False
    choices: List[str] = field(default_factory=list)
    _value: Any = None

    @property
    def value(self):
        return self._value if self._value is not None else self.default

    @value.setter
    def value(self, value):
        self._value = value


class WordlistOption(ModuleOption):
    def __init__(self, name: str, description: str, required: bool = False):
        super().__init__(
            name=name,
            description=description,
            type='wordlist',
            default=None,
            required=required
        )
        self.custom_path: Optional[str] = None

@dataclass
class ModuleBase:
    def __init__(self):
        name: str = ""
        description: str = "No description."
        version: str = "0.1.0"
        category: str = ""
        is_public: bool = False
        authors: List[str] = []
        homepage: str = ""
        license: str = ""
        dependencies: List[str] = []
        min_python_version: str = "3.10"
        tags: List[str] = []
        repository: str = ""
        self.options: List[ModuleOption] = []
        self._ui_elements: Dict[str, ctk.CTkBaseClass] = {}
        self.db = DatabaseManager()
        self._option_values = {}

    @property
    def is_modified(self) -> bool:
        return hasattr(self, '_is_modified') and self._is_modified

    @is_modified.setter
    def is_modified(self, value: bool):
        self._is_modified = value

    def create_ui(self, parent: ctk.CTkBaseClass) -> None:
        """Create custom UI elements for the module"""
        pass

    def get_ui_elements(self) -> Dict[str, ctk.CTkBaseClass]:
        """Get all UI elements created by the module"""
        return self._ui_elements

    def get_option_value(self, name: str) -> Any:
        """Get option value by name"""
        option = next((opt for opt in self.options if opt.name == name), None)
        if option:
            return self._option_values.get(name, option.default)
        return None

    def set_option_value(self, name: str, value: Any) -> None:
        """Set option value by name"""
        self._option_values[name] = value

    def run(self) -> None:
        """Execute the module with current options"""
        pass

class ModuleSecurity:
    """
    Enhanced security checker for Python modules using both AST analysis and Bandit.
    """

    def __init__(
        self, confidence_threshold: str = "HIGH", severity_threshold: str = "MEDIUM"
    ) -> None:
        """
        Initialize the security checker with configurable thresholds.

        Args:
            confidence_threshold: Minimum confidence level for Bandit findings
            severity_threshold: Minimum severity level for Bandit findings
        """
        self.confidence_threshold = confidence_threshold
        self.severity_threshold = severity_threshold

    def run_bandit_analysis(self, file_path: str) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Run Bandit security analysis on a Python file.

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            Tuple containing:
            - List of security issues found
            - Boolean indicating if any critical issues were found
        """
        try:
            # Run bandit with JSON output and default configuration
            cmd = [
                "bandit",
                "-f",
                "json",
                "--severity-level",
                self.severity_threshold.lower(),
                "--confidence-level",
                self.confidence_threshold.lower(),
                "-r",  # Recursive scan
                file_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode not in [0, 1]:  # 1 means issues found
                print(f"Bandit error: {result.stderr}")
                return [], False

            try:
                bandit_results = json.loads(result.stdout)
            except json.JSONDecodeError:
                print("Error: Invalid JSON output from Bandit")
                return [], False

            # Extract relevant findings
            issues = []
            has_critical = False

            for result in bandit_results.get("results", []):
                issue = {
                    "severity": result["issue_severity"],
                    "confidence": result["issue_confidence"],
                    "description": result["issue_text"],
                    "line": result["line_number"],
                    "code": result["code"],
                }
                issues.append(issue)

                if result["issue_severity"] == "HIGH":
                    has_critical = True

            return issues, has_critical

        except Exception as e:
            print(f"Error running Bandit analysis: {str(e)}")
            return [], False

    def check_module_security(self, file_path: str) -> Tuple[List[str], bool]:
        """
        Perform comprehensive security analysis using both AST and Bandit.

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            Tuple containing:
            - List of security warnings
            - Boolean indicating if the module is safe to load
        """
        warnings = []
        is_safe = True

        # Run AST analysis first
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)

            ast_warnings = self.analyze_ast(tree)
            warnings.extend(ast_warnings)

            if any("CRITICAL" in w for w in ast_warnings):
                is_safe = False

        except Exception as e:
            warnings.append(f"Error during AST analysis: {str(e)}")
            is_safe = False

        # Run Bandit analysis
        bandit_issues, has_critical = self.run_bandit_analysis(file_path)
        if bandit_issues:
            warnings.append("Bandit security analysis findings:")
            for issue in bandit_issues:
                warning = (
                    f"- {issue['severity']} severity ({issue['confidence']} confidence): "
                    f"{issue['description']} at line {issue['line']}\n"
                    f"  Code: {issue['code']}"
                )
                warnings.append(warning)

        if has_critical:
            is_safe = False

        return warnings, is_safe

    def analyze_ast(self, tree: ast.AST) -> List[str]:
        """
        Perform custom AST analysis for additional security checks.

        Args:
            tree: AST tree to analyze

        Returns:
            List of warning messages
        """
        warnings = []

        for node in ast.walk(tree):
            # Check for potentially dangerous imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if self.is_dangerous_import(alias.name):
                        warnings.append(
                            f"CRITICAL: Potentially dangerous import detected: {alias.name}"
                        )
            # Check for exec-like calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ["exec", "eval", "__import__"]:
                        warnings.append(
                            f"CRITICAL: Dangerous built-in function call detected: {node.func.id}"
                        )
            # Check for system modifications
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    if self.is_dangerous_attribute_access(node):
                        warnings.append(
                            f"WARNING: Potentially dangerous system modification: "
                            f"{node.value.id}.{node.attr}"
                        )
        return warnings

    @staticmethod
    def is_dangerous_import(import_name: str) -> bool:
        """Check if an import is potentially dangerous."""
        dangerous_imports = {
            "subprocess",
            "os.system",
            "pickle",
            "marshal",
            "shelve",
            "tempfile",
            "shutil",
        }
        return any(imp in import_name for imp in dangerous_imports)

    @staticmethod
    def is_dangerous_attribute_access(node: ast.Attribute) -> bool:
        """Check if an attribute access is potentially dangerous."""
        dangerous_patterns = [
            ("os", ["system", "popen", "spawn", "fork"]),
            ("sys", ["modules", "path"]),
            ("subprocess", ["call", "Popen", "run"]),
        ]

        if isinstance(node.value, ast.Name):
            for module, attrs in dangerous_patterns:
                if node.value.id == module and node.attr in attrs:
                    return True
        return False


class ModuleLoader:
    """
    Handles the loading and management of modules, including security checks
    and dependency verification.
    """

    def __init__(self) -> None:
        """Initialize the ModuleLoader with security checker."""
        self.security = ModuleSecurity()
        self.loaded_modules: Dict[str, ModuleBase] = {}
        self.module_paths: Dict[str, str] = {}
        self.db = DatabaseManager()

    def get_base_classes(self, node: ast.ClassDef) -> List[str]:
        """
        Extract base class names from a ClassDef AST node.

        Args:
            node (ast.ClassDef): The AST node representing a class definition

        Returns:
            List[str]: List of base class names
        """
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                parts = []
                current = base
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                bases.append(".".join(reversed(parts)))
        return bases

    def find_module_classes(self) -> List[str]:
        """
        Search for Python files containing ModuleBase-derived classes.

        Returns:
            List[str]: List of file paths containing potential modules
        """

        python_files = []
        script_dir = Path(__file__).parent
        modules_dir = script_dir / "modules"

        if not modules_dir.exists():
            print(f"Warning: Modules directory not found at {modules_dir}")
            return python_files

        for file_path in modules_dir.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            base_classes = self.get_base_classes(node)
                            if "ModuleBase" in base_classes:
                                python_files.append(str(file_path))
                                break
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
        return python_files

    def check_dependencies(self, module: ModuleBase) -> bool:
        """
        Verify that all dependencies for a module are satisfied.

        Args:
            module (ModuleBase): Module to check dependencies

        Returns:
            bool: True if all dependencies are satisfied
        """
        for dependency in module.dependencies:
            try:
                importlib.import_module(dependency)
            except ImportError:
                print(f"Missing dependency for {module.name}: {dependency}")
                return False
        return True

    def verify_python_version(self, module: ModuleBase) -> bool:
        """
        Check if the current Python version meets the module's requirements.

        Args:
            module (ModuleBase): Module to check version requirements

        Returns:
            bool: True if Python version is compatible
        """
        current_version = tuple(map(int, sys.version.split(".")[0:2]))
        required_version = tuple(map(int, module.min_python_version.split(".")[0:2]))
        return current_version >= required_version

    def load_module(self, file_path: str) -> Optional[ModuleBase]:
        """
        Load a single module after performing security and compatibility checks.

        Args:
            file_path (str): Path to the module file

        Returns:
            Optional[ModuleBase]: Loaded module instance if successful
        """
        try:
            # Security check
            warnings, is_safe = self.security.check_module_security(file_path)

            if warnings:
                print("\nSecurity Analysis Results:")
                for warning in warnings:
                    print(warning)

            if not is_safe:
                print("\nModule failed security checks.")
                response = input("Do you want to load this module anyway? (y/N): ")
                if response.lower() != "y":
                    return None

            # Load the module
            module_name = Path(file_path).stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module from {file_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find and instantiate the ModuleBase-derived class
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (
                    isinstance(item, type)
                    and issubclass(item, ModuleBase)
                    and item != ModuleBase
                ):
                    module_instance = item()

                    # Verify compatibility
                    if not self.verify_python_version(module_instance):
                        print(
                            f"Module {module_instance.name} requires Python {module_instance.min_python_version} or higher"
                        )
                        return None

                    if not self.check_dependencies(module_instance):
                        print(
                            f"Module {module_instance.name} has unsatisfied dependencies"
                        )
                        return None

                    # Register in database
                    module_data = {
                        'name': module_instance.name,
                        'category': module_instance.category,
                        'description': module_instance.description,
                        'version': module_instance.version,
                        'authors': module_instance.authors,
                        'dependencies': module_instance.dependencies,
                    }

                    module_id = self.db.register_module(module_data, Path(file_path))
                    module_instance.id = module_id

                    if not self.db.verify_module(module_instance.id, Path(file_path)):
                        module_instance.is_modified = True

                    return module_instance

        except Exception as e:
            print(f"Error loading module {file_path}: {str(e)}")
            return None

    def load_all_modules(self) -> Dict[str, ModuleBase]:
        """
        Load all available modules from the modules directory.

        Returns:
            Dict[str, ModuleBase]: Dictionary of loaded modules
        """
        self.loaded_modules.clear()
        self.module_paths.clear()

        module_files = self.find_module_classes()

        for file_path in module_files:
            module = self.load_module(file_path)
            if module is not None:
                self.loaded_modules[module.name] = module
                self.module_paths[module.name] = file_path
                print(f"Successfully loaded module: {module.name}")

        return self.loaded_modules

    def reload_module(self, module_name: str) -> Optional[ModuleBase]:
        """
        Reload a specific module;

        Args:
            module_name (str): Name of the module to reload

        Returns:
            Optional[ModuleBase]: Reloaded module instance if successful
        """
        if module_name not in self.module_paths:
            print(f"Module {module_name} not found")
            return None

        file_path = self.module_paths[module_name]
        module = self.load_module(file_path)

        if module is not None:
            self.loaded_modules[module_name] = module
            print(f"Successfully reloaded module: {module_name}")

        return module

    def get_module(self, module_name: str) -> Optional[ModuleBase]:
        """
        Get a loaded module by name.

        Args:
            module_name (str): Name of the module to retrieve

        Returns:
            Optional[ModuleBase]: The requested module instance if found
        """
        return self.loaded_modules.get(module_name)

    def list_modules(self) -> List[Dict[str, Any]]:
        """
        Get information about all loaded modules.

        Returns:
            List[Dict[str, Any]]: List of module information dictionaries
        """
        return [
            {
                "name": module.name,
                "description": module.description,
                "version": module.version,
                "category": module.category,
                "authors": module.authors,
                "is_public": module.is_public,
            }
            for module in self.loaded_modules.values()
        ]
