import importlib
import pkgutil


def load_submodules(package):
    """Dynamically imports all submodules of a package."""
    for loader, module_name, is_pkg in pkgutil.walk_packages(
            package.__path__,
            package.__name__ + "."
    ):
        # Import the module and ensure it's registered in sys.modules
        importlib.import_module(module_name)
