import os
import sys
import types
import typing
import inspect
import importlib.util



def load_module(name: str, path: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def find_module_classes(module: types.ModuleType) -> list[typing.Type]:
    classes: list[type] = []
    for _, clstype in inspect.getmembers(module, inspect.isclass):
        # Ignore core blocks, they don't have functionality
        if "jabuti.core" in clstype.__module__:
            continue
        
        classes.append(clstype)
    return classes


def find_path_module_classes(path: str) -> list[typing.Type]:
    all_classes = []
    for root, _, files in os.walk(path):
        if "__pycache__" in root:
            continue
        
        cln_root = root.replace('\\', '/')
        module_name = cln_root.removeprefix('./').removesuffix('/').replace('/', '.')
        root_path = cln_root.removesuffix('/')
        
        for file in files:
            file_name = file.removesuffix('.py')
            scope = f"{module_name}.{file_name}"
            file_path = f"{root_path}/{file}"
            
            module = load_module(scope, file_path)
            classes = find_module_classes(module)
            all_classes.extend(classes)
    
    return all_classes


def describe_class(cls: typing.Type) -> dict[str, str]:
    macro = cls.__module__.split('.')[0]
    scope = cls.__module__#.removeprefix(f"{macro}.")
    group = scope.split('.')[-1]
    name = cls.__name__
    desc = {
        "macro": macro,
        "scope": scope,
        "group": group,
        "name": name,
        "full": f"{scope}.{name}",
        "class": cls,
    }
    return desc


def find_full_classes(
        module_or_path: list[types.ModuleType | str],
    ) -> dict[str, dict[str, str]]:
    classes = []
    clsdesc = {}
    
    for mop in module_or_path:
        if isinstance(mop, str):
            cls = find_path_module_classes(mop)
            classes.extend(cls)
        elif isinstance(mop, types.ModuleType):
            cls = find_module_classes(mop)
            classes.extend(cls)
        else:
            print(f"Not found: {mop}")
    
    for cls in classes:
        desc = describe_class(cls)
        name = desc.pop("full")
        clsdesc[name] = desc
    
    return clsdesc



if __name__ == "__main__":
    import jabuti as jb
    
    clsdesc = find_full_classes([jb.builtin, "./custom/"])
    for k, v in clsdesc.items():
        print(f"{k: <32}: {v}")
