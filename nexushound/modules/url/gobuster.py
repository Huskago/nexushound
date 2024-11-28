from dataclasses import dataclass, field
from typing import List

from nexushound.modules_manager import ModuleBase


@dataclass
class GoBuster(ModuleBase):
    name: str = "GoBuster"
    description: str = "A directory/file & DNS busting tool"
    version: str = "0.1.0"
    is_public: bool = True
    authors: List[str] = field(default_factory=lambda: ["Nexushound"])
    homepage: str = ""
    license: str = "MIT"
    dependencies: List[str] = field(default_factory=lambda: ["requests"])
    min_python_version: str = "3.10"
    category: str = "URL"
    tags: List[str] = field(
        default_factory=lambda: ["bruteforce", "directory", "file", "dns"]
    )
    repository: str = ""
