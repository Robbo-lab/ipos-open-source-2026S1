import inspect
import os
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from fastapi import APIRouter, HTTPException


class Router:

    # Routers must have the word "_router" in it

    system_router = APIRouter(prefix="", tags=["system"])
    task_router = APIRouter(prefix="", tags=["task"])

    @classmethod
    def load_all_routes(cls):
        for root, _dirs, files in os.walk("app/routes"):
            for file in files:

                file_path = os.path.join(root, file)
                try:
                    if "__pycache__" in file_path:
                        continue

                    if Path(file_path).name.startswith("route_"):
                        module_name = Path(file_path).stem
                        spec = spec_from_file_location(module_name, file_path)
                        module = module_from_spec(spec)
                        spec.loader.exec_module(module)

                except (UnicodeDecodeError, PermissionError):
                    continue

    @classmethod
    def add_routes_to_app(cls, app):
        print("Adding routes to app")
        for name, prop in inspect.getmembers(cls):
            if inspect.ismethod(prop) or inspect.isfunction(prop):
                continue

            if "_router" in name:
                print(name)
                app.include_router(prop)

    @classmethod
    def get_router(cls, router_name):
        if "router" in router_name:
            try:
                return getattr(cls, router_name)
            except ModuleNotFoundError as err:
                raise HTTPException(status_code=404,
                                    detail="Router not found") from err
        else:
            try:
                return getattr(cls, router_name + "_router")
            except ModuleNotFoundError as err:
                raise HTTPException(status_code=404,
                                    detail="Router not found") from err
