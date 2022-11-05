import json
from urllib.parse import urlparse
from pathlib import Path

from multiprocessing.pool import TERMINATE
from typing import TYPE_CHECKING, Any
from poetry.console.application import Application
from poetry.console.commands.install import InstallCommand
from poetry.console.commands.update import UpdateCommand
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.installation.installer import Installer
from cleo.helpers import option
from cleo.events.console_events import COMMAND, TERMINATE
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_terminate_event import ConsoleTerminateEvent
from cleo.events.event_dispatcher import EventDispatcher

from .build_info_executor import BuildInfoExecutor
from .artifactory_client import ArtifactoryClient

class BuildInfoPlugin(ApplicationPlugin):

    def __init__(self) -> None:
        super().__init__()
        self._application = None

    def activate(self, application: Application) -> None:
        self._application = application
        application.event_dispatcher.add_listener(COMMAND, self.inject_build_event_installer)
        application.event_dispatcher.add_listener(TERMINATE, self.output_build_log)

    def _is_pertinent_command(self, obj: Any):
        return isinstance(obj, InstallCommand) or isinstance(obj, UpdateCommand)

    def inject_build_event_installer(
        self,
        event: ConsoleCommandEvent,
        event_name: str,
        dispatcher: EventDispatcher
        ):

        if not self._is_pertinent_command(event.command):
            return

        event.io.write_line("<info>Deploying BuildInfoInstallInstaller</info>")
        
        executor = BuildInfoExecutor.from_executor(
            event.command.installer.executor
        )

        installer = Installer(
            event.io,
            event.command.env,
            event.command.installer._package,
            event.command.installer._locker,
            event.command.installer.executor._chooser._pool,
            event.command.installer.executor._authenticator._config,
            event.command.installer._installed_repository,
            executor,
            False  # TOOD: find disable cache setting
        )
        installer.use_executor(executor)

        event.command.set_installer(installer)

    def output_build_log(
        self, 
        event: ConsoleTerminateEvent,
        event_name: str,
        dispatcher: EventDispatcher
    ):
        if self._is_pertinent_command(event.command):

            client = ArtifactoryClient()
            package = self._application.poetry.package
            package_id = f"{package.pretty_name}:{package.pretty_version}"
            build_info = {
                "modules": [{
                    "id": package_id,
                    "type": "python",
                    "dependencies": []
                }]
            }

            log = event.command.installer.executor._operation_log

            for dependency in log:
                dp = dependency["package"]
                wheel_url = urlparse(dependency["url"])
                wheel_path = Path(wheel_url.path)
                wheel_name = wheel_path.parts[-1]
                event.io.write_line(f"<info>Querying Artifactory for {wheel_name} </info>")
                package_info = client.get_artifact(wheel_name)
                entry = {
                    "id": f"{dp.pretty_name}:{package.pretty_version}",
                    "type": dp.source_type if dp.source_type is not None else "whl",
                    "requestedBy": [self._application.poetry.package.pretty_name],
                    "sha1": package_info[0]["actual_md5"],
                    "sha256": package_info[0]["sha256"],
                    "md5": package_info[0]["actual_md5"]
                }

                requested_by = self._get_requested_by(dp.pretty_name, log)
                if requested_by is not None:
                    entry["requestedBy"].extend(requested_by)

                build_info["modules"][0]["dependencies"].append(entry)

            event.io.write_line(f"<info>Writing build log for {package_id}</info>")
            with open("./build-log.json", "w") as file:
                json.dump(build_info, file, indent=4)

    def _get_requested_by(self, package_name, log):
        retval = []
        for dependency in log:
            if package_name in [p.name for p in dependency["package"].all_requires]:
                retval.append(self._format_package(dependency["package"]))
                retval.extend(self._get_requested_by(dependency["package"].pretty_name, log))
        return retval

    def _format_package(self, package):
        return f"{package.pretty_name}:{package.pretty_version}"
