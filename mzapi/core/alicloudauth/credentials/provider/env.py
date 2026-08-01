
from .refreshable import Credentials
from .refreshable import ICredentialsProvider
from \.\.\. auth_util
from ..exceptions import CredentialException


class EnvironmentVariableCredentialsProvider(ICredentialsProvider):

    def get_credentials(self) -> Credentials:

        access_key_id = auth_util.environment_access_key_id
        access_key_secret = auth_util.environment_access_key_secret
        security_token = auth_util.environment_security_token

        if access_key_id is None or len(access_key_id) == 0:
            raise CredentialException("Environment variable accessKeyId cannot be empty")

        if access_key_secret is None or len(access_key_secret) == 0:
            raise CredentialException("Environment variable accessKeySecret cannot be empty")

        return Credentials(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            security_token=security_token,
            provider_name=self.get_provider_name()
        )

    async def get_credentials_async(self) -> Credentials:
        return self.get_credentials()

    def get_provider_name(self) -> str:
        return 'env'
