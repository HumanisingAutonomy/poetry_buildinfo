import json

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
        dispactcher: EventDispatcher
    ):
        if self._is_pertinent_command(event.command):
            event.io.write_line("<info>Writing build log</info>")
            with open("./build-log.json", "w") as file:
                json.dump(event.command.installer.executor._operation_log, file)