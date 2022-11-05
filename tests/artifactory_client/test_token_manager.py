import pytest

from poetry_buildinfo.artifactory_client._token_manager import TokenManager
from poetry_buildinfo.artifactory_client._model import TokenResponse

class TestTokenManager:

    @pytest.fixture
    def mock_config(self):
        class MockConfigManager:
            def write_global_config(self):
                pass
            
            artifactory_url = "http://example.com/artifactory/"
            access_token = "AccessToken"
            refresh_token = "RefreshToken"
            
        return MockConfigManager()

    @pytest.fixture
    def token_manager(self, mock_config):
        return TokenManager(mock_config)

    @pytest.fixture
    def token_response(self):
        return TokenResponse(
            access_token="RefreshedAccessToken",
            refresh_token="RefehsedRefreshToken",
            scope="access_groups",
            token_type="Bearer",
            expires_in=60
        )

    def test_renew_token(self, token_manager, requests_mock, token_response):
        requests_mock.post("http://example.com/artifactory/api/security/token", text=token_response.json(by_alias=True))
        token_manager._renew_token()
        assert requests_mock.called
        call = requests_mock.last_request
        assert call.headers["Content-Type"] == "application/x-www-form-urlencoded"
        print(call.text)