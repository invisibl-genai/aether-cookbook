from constants import LLM_PROVIDERS


class LLMProviderNotFoundException(Exception):
    message = f"The LLM provider must be one of the following: {LLM_PROVIDERS}"


class NoResponseException(Exception):
    message = "The LLM did not return a response."
