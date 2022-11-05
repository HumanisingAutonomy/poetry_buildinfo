from datetime import datetime
from pydantic import BaseModel, Field

class Server(BaseModel):
    url: str
    user: str
    password: str
    artifactory_url: str = Field(alias="artifactoryUrl")
    distribution_url: str = Field(alias="distributionUrl")
    xray_url: str = Field(alias="xrayUrl")
    mission_control_url: str = Field(alias="missionControlUrl")
    pipelines_url: str = Field(alias="pipelinesUrl")
    access_token: str = Field(alias="accessToken")
    artifactory_refresh_token: str = Field(alias="artifactoryRefreshToken")
    server_id: str = Field(alias="serverId")
    is_default: bool = Field(alias="isDefault")


class GlobalConfig(BaseModel):
    version: int
    servers: list[Server]
    
    @property
    def default_server(self) -> Server:
        return [server for server in self.servers if server.is_default][0]

    def get_server(self, server_id: str):
        return [server for server in self.servers if server.server_id == server_id][0]

class Resolver(BaseModel):
    repo: str
    server_id: str = Field(alias="serverId")


class LocalConfig(BaseModel):
    version: int
    type: str
    resolver: Resolver


class TokenRequest(BaseModel):
    access_token: str
    refresh_token: str
    grant_type: str = Field(default="refresh_token")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    scope: str
    token_type: str


class TokenPayload(BaseModel):
    subject: str = Field(alias="sub")
    scope: str = Field(alias="scp")
    audience: str = Field(alias="aud")
    issuer: str = Field(alias="iss")
    expire_time: int = Field(alias="exp")
    issued_at_time: int = Field(alias="iat")
    identifier: str = Field(alias="jti")

    @property
    def expiration(self) -> datetime:
        return datetime.fromtimestamp(self.expire_time)

    @property
    def expired(self) -> bool:
        print(f"Expired at {self.expiration}, now is {datetime.now()}.")
        return self.expiration < datetime.now()

    @property
    def issued_at(self) -> datetime:
        return datetime.fromtimestamp(self.issued_at_time)