import requests
from urllib.parse import urljoin

from ._config_manager import ConfigManager
from ._token_manager import TokenManager


class ArtifactoryClient:
    def __init__(self, config_manager: ConfigManager = None, token_manager = None):
        self._config_manager = config_manager if config_manager is not None else ConfigManager()
        self._token_manager = token_manager if token_manager is not None else TokenManager(self._config_manager)

    PIP_AQL_FORMAT = 'items.find({{"repo":"{repo}", "$or": [{{ "name": {{ "$match": "{name}" }} }}]}}).include("name","repo","path","actual_sha1","actual_md5","sha256")'

    def get_artifact(self, name: str):
        query = self.PIP_AQL_FORMAT.format(repo=self._config_loader.repo, name=name)
        url = urljoin(self._config_loader.server.artifactory_url, "api/search/aql")
        response = requests.post(url, query, headers=self._token_manager.auth_headers())
        response.raise_for_status()

        try:
            return response.json()["results"]
        except KeyError as error:
            return response.text

