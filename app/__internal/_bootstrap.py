import glob
import traceback
from importlib import util
import os.path
import sys

from fastapi.responses import RedirectResponse


class Logger:
    def __init__(self, service: str):
        self.service = service

    def info(self, *msg):
        self._log("INFO", *msg)

    def warn(self, *msg):
        self._log("WARN", *msg)

    def debug(self, *msg):
        self._log("DEBU", *msg)

    def verbose(self, *msg):
        self._log("VERB", *msg)

    def _log(self, typ: str, *msg):
        print(f"[{typ}] {self.service}: {' '.join([str(x) for x in msg])}")


class Function:
    __log = None

    @staticmethod
    def _dummy_function():
        ...

    @property
    def log(self):
        if not self.__log:
            self.__log = Logger(f"{self.__class__.__name__}")
        return self.__log


class ConfigBase:
    def __init__(self, autoload=True):
        if autoload:
            self.Load()

    def Load(self):
        for x in self.__dir__():
            if x.startswith("__"):
                continue
            if callable(getattr(self, x)):
                continue
            if method := getattr(self, f"resolve_{x}", None):
                self.__dict__[x] = method()
            else:
                self.__dict__[x] = os.getenv(x, getattr(self, x))
        try:
            with open(".env") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                x = line.split("=")
                if len(x) == 2:
                    self.__dict__[x[0]] = x[1]
                else:
                    print(f"Warning: .env produced an invalid entry in line {i + 1}")
        except FileNotFoundError:
            ...

        return self


def bootstrap(app):
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    bootstraps = []

    @app.get("/stage")
    def stage():
        return os.getenv("stage", "development")

    @app.get("/")
    def status():
        return RedirectResponse("/docs")

    """
    Look for files inside of the './app/functions' directory and 
    attempt to load any classes that has 'Function' subclassed.
    """
    for fn_str in glob.glob(os.path.join("src", "api", "**.py")):
        print("Loading", fn_str)
        module_name = os.path.split(fn_str)[-1].replace(".py", "")
        spec = util.spec_from_file_location(module_name, fn_str)
        module = util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        fn = None
        print(dir(module))
        for attr_str in dir(module):
            attr = getattr(module, attr_str)
            if "_bootstrap.Function" in f"{attr}":
                continue
            if getattr(attr, "_dummy_function", None):
                print("Setting fn to ", attr)
                fn = attr

        if fn:
            if (getattr(module, "__init__", None)) is not None:
                print("Initializing:", fn)

                def error(*msg: any, warn=False):
                    if warn:
                        warnings.append(
                            {"info": " ".join(msg), "function": module_name}
                        )
                        return
                    errors.append({"info": " ".join(msg), "function": module_name})

                try:
                    fn = fn(error)
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    errors.append(
                        {
                            "info": f"Init raised an exception: {''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))}",
                            "function": module_name,
                        }
                    )

            if (getattr(fn, "Bootstrap", None)) is not None:
                bootstraps.append({"class": fn, "name": module_name})

    """
    Check if there are errors thrown that aren't warnings. These errors are generated by the Init method.
    Warnings would still let the modules load but errors would not.
    """
    if not errors:
        for bs in bootstraps:
            print(f"Bootstrapping: {bs['name']}")
            bs["class"].Bootstrap(app)
    else:
        print("ERROR: FUNCTIONS FAILED TO START\n\tCheck /docs for more info")
        app.description += """\n\n***Error: API Failed to start***\n"""
        for err in errors:
            trace = err["info"].replace("\n", "\n\t\t")
            app.description += f"\n\t[{err['function']}]: {trace}"

    if warnings:
        app.description += """\n\n***API Returned warnings***\n"""
        for err in warnings:
            trace = err["info"].replace("\n", "\n\t\t")
            app.description += f"\n\t[{err['function']}]: {trace}"
