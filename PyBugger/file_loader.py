import importlib


def load_py_file(file_path):
    if ".py" in file_path:
        file_path = file_path.replace(".py", "")
    return importlib.import_module(file_path)

