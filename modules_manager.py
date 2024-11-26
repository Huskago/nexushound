import ast
import os
from pathlib import Path
from typing import List


def get_base_classes(node: ast.ClassDef) -> List[str]:
    """
    Extract base class names from a ClassDef AST node.

    Args:
        node (ast.ClassDef): The AST node representing a class definition

    Returns:
        List[str]: List of base class names, including full path for qualified names

    Example:
        For a class definition like 'class MyModule(ModuleBase)',
        it will return ['ModuleBase']
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


def find_module_classes() -> List[str]:
    """
    Search for Python files containing classes that inherit from ModuleBase.
    Seaches in the 'modules' directory relative to the script's location.

    Returns:
        List[str]: List of file paths containing ModuleBase-derived classes

    Note:
        Uses the script's directory as the base path to ensure consistent behavior
        regardless of where the script is run from.
    """

    python_files = []
    # Get the directory where the script is located
    script_dir = Path(__file__).parent
    modules_dir = script_dir / "modules"

    # Ensure the modules directory exists
    if not modules_dir.exists():
        print(f"Warning: Modules directory not found at {modules_dir}")
        return python_files

    for root, _, files in os.walk(modules_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            base_classes = get_base_classes(node)
                            if "ModuleBase" in base_classes:
                                python_files.append(file_path)
                                break
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                    continue

    return python_files
