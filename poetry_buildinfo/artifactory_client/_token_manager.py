import requests
from urllib.parse import urljoin
from ._model import TokenRequest, TokenPayload, TokenResponse
from dataclasses import asdict
import base64

from ._config_manager import ConfigManager


class TokenManager:

    _config: ConfigManager

    def __init__(self, config_manager: ConfigManager = None):
        self._config = config_manager if config_manager is not None else ConfigManager()

    def _renew_token(self):
        request = TokenRequest(
            access_token=self._config.access_token,
            refresh_token=self._config.refresh_token,
            grant_type="refresh_token"
        )
        url = urljoin(self._config.artifactory_url, "api/security/token")
        request_dict = request.dict(by_alias=True)
        print(request_dict)
        response = requests.post(url, data=request_dict)
        response.raise_for_status()
        token_response = TokenResponse.parse_raw(response.text, content_type="application/json")
        # TODO: sort out locking
        self._config.access_token = token_response.access_token
        self._config.refresh_token = token_response.refresh_token
        self._config.write_global_config()

    
    def _extract_payload_from_token(self, token: str):
        token_parts = token.split(".")

        if len(token_parts) != 3:
            raise ValueError("Cannot decode provided token.")

        payload = base64.standard_b64decode(token_parts[1] + "=" * ( len(token_parts[1]) % 4 ) ).decode("utf-8")
        return TokenPayload.parse_raw(payload)

    def _token_expired(self) -> bool:
        return self._token_payload().expired

    def _token_payload(self) -> TokenPayload:
        return self._extract_payload_from_token(self._config.access_token)

    def auth_headers(self):
        # TODO: sort out locking
        if self._token_expired():
            self._renew_token()

        return {
            "Authorization": f"Bearer {self._config.access_token}"
        }
