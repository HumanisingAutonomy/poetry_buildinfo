from typing import TYPE_CHECKING

from poetry.installation.installer import Installer

from .build_info_executor import BuildInfoExecutor

if TYPE_CHECKING:
    from collections.abc import Iterable

    from cleo.io.io import IO
    from packaging.utils import NormalizedName
    from poetry.core.packages.project_package import ProjectPackage

    from poetry.config.config import Config
    from poetry.installation.executor import Executor
    from poetry.packages import Locker
    from poetry.utils.env import Env
    from poetry.repositories import Pool
    from poetry.repositories import Repository

class BuildInfoInstaller(Installer):

    def __init__(self, io: IO, env: Env, package: ProjectPackage, locker: Locker, pool: Pool, config: Config, installed: Repository | None = None, executor: Executor | None = None, disable_cache: bool = False) -> None:
        if executor is None:
            executor = BuildInfoExecutor(env, pool, config, io, disable_cache=disable_cache)
        super().__init__(io, env, package, locker, pool, config, installed, executor, disable_cache)


    