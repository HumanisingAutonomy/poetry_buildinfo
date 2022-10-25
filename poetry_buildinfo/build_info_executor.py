from ast import operator
from typing import TYPE_CHECKING
from poetry.installation.executor import Executor
from cleo.io.io import IO
from poetry.config.config import Config
from poetry.repositories import Pool
from poetry.utils.env import Env
from poetry.installation.operations import Install, Update


class BuildInfoExecutor(Executor):
    def __init__(self, env: Env, pool: Pool, config: Config, io: IO, parallel: bool | None = None, disable_cache: bool = False) -> None:
        super().__init__(env, pool, config, io, parallel, disable_cache)
        self._operation_log = []


    @staticmethod
    def from_executor(executor: Executor):
        return BuildInfoExecutor(
            executor._env,
            executor._chooser._pool,
            executor._authenticator._config,
            executor._io,
            False,  # TODO: find cache disable setting
        )

    def _log_operation(self, operation: str, package: str, url: str):
        return self._operation_log.append({
            "operation": operation,
            "package": package.pretty_name,
            "type": package.source_type,
            "url": url
        })

    def _install(self, operation: Install | Update):
        url = self._chooser.choose_for(operation.package).url
        self._log_operation(
            operation.job_type,
            operation.package,
            url
            )
        super()._install(operation)
