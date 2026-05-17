from __future__ import annotations

from backend.config.env_vars import EnvVars
from backend.utils.singleton_meta import SingletonMeta


class EnvVarManager(metaclass=SingletonMeta):
    def __init__(self, **kwargs):
        if self._env_vars is not None:
            self._env_vars = EnvVars(**kwargs)

    @property
    def env_vars(self) -> EnvVars:
        return self._env_vars
