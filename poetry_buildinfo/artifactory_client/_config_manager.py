import json
import os
import yaml
from ._model import GlobalConfig, LocalConfig, Server

class ConfigManager:
    _global_path: str
    _global_config: GlobalConfig
    _local_config: LocalConfig
    
    def __init__(self, 
        global_path: str = "~/.jfrog/jfrog-cli.conf.v6",
        local_path: str = ".jfrog/projects/poetry.yaml"):
        
        self._global_path = os.path.expanduser(global_path)
        with open(self._global_path, "r", encoding="UTF-8") as file:
            config_data = json.loads(file.read())
            self._global_config = GlobalConfig(**config_data)

        self._local_path = os.path.expanduser(local_path)
        with open(self._local_path, "r", encoding="UTF-8") as file:
            config_data = yaml.safe_load(file.read())
            self._local_config = LocalConfig(**config_data)

    @property
    def global_config(self) -> GlobalConfig:
        return self._global_config

    @property
    def local_config(self) -> LocalConfig:
        return self._local_config

    @property
    def server(self) -> Server:
        return self._global_config.get_server(self._local_config.resolver.server_id)

    @property
    def artifactory_url(self) -> str:
        return self.server.artifactory_url

    @property
    def access_token(self) -> str:
        return self.server.access_token

    @access_token.setter
    def access_token(self, token: str) -> None:
        self.server.access_token = token

    @property
    def refresh_token(self) -> str:
        return self.server.artifactory_refresh_token

    @refresh_token.setter
    def refresh_token(self, token: str) -> None:
        self.server.artifactory_refresh_token = token

    def write_global_config(self):
        with open(self._global_path, "w", encoding="utf-8") as file:
            file.write(self._global_config.json(by_alias=True, dumps_kwargs={"indent": 4}))
        return

    @property
    def repo(self) -> str:
        return self._local_config.resolver.repo
