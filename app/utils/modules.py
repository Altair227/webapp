from flask import Blueprint, Flask
import importlib
import pkgutil
from types import ModuleType


def register_child_blueprints(
    parent_bp: Blueprint | Flask,
    modules_package: ModuleType,
    *,
    routes_module_name: str = "routes",
    blueprint_name: str = "bp",
) -> None:
    package_path = getattr(modules_package, "__path__", None)
    if package_path is None:
        return
    package_prefix = modules_package.__name__ + "."
    for module_info in pkgutil.iter_modules(package_path, package_prefix):
        if not module_info.ispkg:
            continue
        routes_module = f"{module_info.name}.{routes_module_name}"
        try:
            module = importlib.import_module(routes_module)
        except ModuleNotFoundError:
            continue
        bp = getattr(module, blueprint_name, None)
        if isinstance(bp, Blueprint):
            parent_bp.register_blueprint(bp)
