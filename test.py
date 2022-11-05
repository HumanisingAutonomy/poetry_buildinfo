from poetry_buildinfo import ArtifactoryClient

if __name__ == "__main__":
    client = ArtifactoryClient()
    client._token_manager._renew_token()
    print(client.get_artifact("typing_extensions-4.4.0*"))
    