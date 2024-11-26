class ModuleBase:
    """
    Base class for all modules in the system.
    Modules must inherit from this class to be recognized by the module finder.

    Properties:
        name (str): Module name, automatically set to class name
        description (str): Module description
        version (str): Module version following semantic versioning
        is_public (bool): Whether the module is intended for public use
        authors (List[str]): List of module authors
        homepage (str): URL to module's homepage or documentation
        license (str): Module's license identifier
        dependencies (List[str]): Required dependencies for the module
        min_python_version (str): Minimum Python version required
        tags (List[str]): Categories or tags for module classification
        repository (str): URL to source code repository
    """

    def __init__(self) -> None:
        self.name = self.__class__.__name__
        self.description = "No description."
        self.version = "0.1.0"
        self.is_public = False
        self.authors = []
        self.homepage = ""
        self.license = ""
        self.dependencies = []
        self.min_python_version = "3.10"
        self.tags = []
        self.repository = ""
