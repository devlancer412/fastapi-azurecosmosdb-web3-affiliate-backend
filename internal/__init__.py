from typing import List
import os
import json

UNSET = "CONFIG-NULL"

class ConfigBase:
    def __init__(self, autoload=True):
        if autoload:
            self.Load()

    def Load(self):
        for x in self.__dir__():
            if x.startswith("__"): continue
            if callable(getattr(self, x)): continue
            if method := getattr(self, f"resolve_{x}", None):
                self.__dict__[x] = method()
            else:
                self.__dict__[x] = os.getenv(x, getattr(self, x))
        try:
            with open(".env") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                x = line.strip().split("=")
                if len(x) == 2:
                    self.__dict__[x[0]] = x[1]
                else:
                    print(f"Warning: .env produced an invalid entry in line {i + 1}")
        except FileNotFoundError:
            ...

        return self

    def has_unset(self) -> List[str]:
        r = []
        for k, v in self.__dict__.items():
            if v == UNSET:
                r.append(k)

        return r
    
