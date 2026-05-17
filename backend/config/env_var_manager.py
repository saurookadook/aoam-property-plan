from __future__ import annotations

from config.env_vars import EnvVars
from utils.singleton_meta import SingletonMeta


class EnvVarManager(metaclass=SingletonMeta):
    def __init__(self, **kwargs):
        if getattr(self, "_env_vars", None) is None:
            self._env_vars = EnvVars(**kwargs)

    @property
    def env_vars(self) -> EnvVars:
        return self._env_vars
