from pydantic import BaseModel


class SecretVariables(BaseModel):
    """Variables required from the ENV to run this example."""

    aether_api_key: str
    aether_proxy_endpoint: str
    azure_api_key: str
    azure_endpoint: str
    azure_openai_api_version: str
    azure_provider_deployment: str
    google_api_key: str
