from google.api_core.exceptions import GoogleAPIError
from openai import APIError


def handle_gemini_exception(exc: GoogleAPIError) -> str:
    """Handle exceptions from the Gemini client.

    Args
    ----
    exc: GoogleAPICallError
        The exception from the Google API call.

    Returns
    -------
    message: str
        The string to be displayed on the Streamlit UI.
    """

    message = exc.response.json().get("error", {}).get("message", repr(exc))

    return message


def handle_azure_exception(exc: APIError) -> str:
    """Handle exceptions from the Azure client.

    Args
    ----
    exc: openai.APIError
        The exception from the Azure OpenAI API call.

    Returns
    -------
    message: str
        The string to be displayed on the Streamlit UI.
    """

    return exc.body.get("message", repr(exc))
