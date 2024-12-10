import logging
import os
from typing import Literal, Union

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPIError
from openai import APIError as OpenAIAPIError
from openai import AzureOpenAI

from constants import GOOGLE_GENERATIVEAI_MODELS, LLM_PROVIDERS
from exceptions import LLMProviderNotFoundException, NoResponseException
from schemas import SecretVariables
from utils import handle_azure_exception, handle_gemini_exception

load_dotenv(override=True)  # Load the environment variables from a `.env` file.

logger = logging.getLogger()

# Initialize variables required from environment variables.
secret_variables = SecretVariables(
    aether_api_key=os.getenv("AETHER_API_KEY"),  # type: ignore
    aether_proxy_endpoint=os.getenv("AETHER_PROXY_ENDPOINT"),  # type: ignore
    azure_api_key=os.getenv("AZURE_API_KEY"),  # type: ignore
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),  # type: ignore
    azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    azure_provider_deployment=os.getenv("AZURE_PROVIDER_MODEL"),  # type: ignore
    google_api_key=os.getenv("GOOGLE_API_KEY"),  # type: ignore
)


def _google_generate(prompt: str, model_name: str, is_enterprise_mode: bool) -> str:
    """Call the Gemini SDK's `.generate_content` method.

    Use the Aether proxy if `is_enterprise_mode` is set; call the Gemini API directly if
    not.

    Args
    ----
    prompt: str
        The prompt to be given to the LLM.
    model_name: str
        The name of the LLM to call using the Gemini SDK.
    is_enterprise_mode: bool
        If true, use the Aether proxy. Otherwise, call the Gemini API directly.

    Returns
    -------
    message: str
        The text to be displayed on the Streamlit UI. The response from the LLM if the
        call goes through; or the error message if it doesn't.
    """

    if is_enterprise_mode:
        # If enterprise mode is selected, pass the Aether API key and Aether proxy
        # endpoint to the Gemini client.
        genai.configure(
            api_key=secret_variables.aether_api_key,
            transport="rest",
            client_options={"api_endpoint": secret_variables.aether_proxy_endpoint},
        )
    else:
        # Otherwise, pass the Google API key and make a call directly to the Gemini API.
        genai.configure(api_key=secret_variables.google_api_key)

    model = genai.GenerativeModel(model_name)
    try:
        response = model.generate_content(prompt)
        logger.info("LLM response: %s", response.text)
        return response.text
    except GoogleAPIError as e:
        logger.exception("Error: %s", repr(e))
        return handle_gemini_exception(exc=e)


def _azure_generate(
    prompt: str, model_name: str, is_enterprise_mode: bool
) -> Union[str, None]:
    """Call the Azure OpenAI SDK's `.chat.completions.create` API.

    Use the Aether proxy if `is_enterprise_mode` is set; call the Azure OpenAI API
    directly if not.

    Args
    ----
    prompt: str
        The prompt to be given to the LLM.
    model_name: str
        The name of the LLM to call using the Azure OpenAI SDK.
    is_enterprise_mode: bool
        If true, use the Aether proxy. Otherwise, call the Azure OpenAI API directly.

    Returns
    -------
    message: str
        The text to be displayed on the Streamlit UI. The response from the LLM if the
        call goes through; or the error message if it doesn't.
    """

    if is_enterprise_mode:
        # If enterprise mode is selected, pass the Aether API key and Aether proxy
        # endpoint to the Azure OpenAI client.
        client = AzureOpenAI(
            api_key=secret_variables.aether_api_key,
            azure_endpoint=secret_variables.aether_proxy_endpoint,
            api_version=secret_variables.azure_openai_api_version,
        )
    else:
        # Otherwise, pass the Azure OpenAI API key and Azure OpenAI endpoint and make
        # the call.
        client = AzureOpenAI(
            api_key=secret_variables.azure_api_key,
            azure_endpoint=secret_variables.azure_endpoint,
            api_version=secret_variables.azure_openai_api_version,
        )

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except OpenAIAPIError as e:
        logger.exception("Error: %s", repr(e))
        return handle_azure_exception(e)


def invoke(
    prompt: str,
    llm_provider: Literal["google-generativeai", "azure-openai"],
    model_name: str,
    is_enterprise_mode: bool,
):
    """Make the call to the LLM.

    Args
    ----
    prompt: str
        The prompt to be given to the LLM.
    llm_provider: "google-generativeai" or "azure-openai"
        The provider of the LLM.
    model_name: str
        The name of the model to use.
    is_enterprise_mode: bool
        If true, use the Aether proxy. Otherwise, call the provider's API directly.

    Returns
    -------
    message: str
        The text to be displayed on the Streamlit UI. The response from the LLM if the
        call goes through; or the error message if it doesn't.
    """

    try:
        if prompt:
            if llm_provider == "google-generativeai":
                response = _google_generate(
                    prompt=prompt,
                    model_name=model_name,
                    is_enterprise_mode=is_enterprise_mode,
                )
            elif llm_provider == "azure-openai":
                response = _azure_generate(
                    prompt=prompt,
                    model_name=model_name,
                    is_enterprise_mode=is_enterprise_mode,
                )

            if response is None:
                raise NoResponseException()

            return response

        return "Your prompt is empty; please re-type your prompt and try again!"

    except Exception as e:
        st.error(f"Error in invoke: {repr(e)}")
        return "An error occurred while processing the request."


# Initialize the session state. Future messages (prompts and LLM responses) will be
# added to the session state.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "response": "How may I assist you today?"}
    ]

# Set up the side-bar components:
# - a checkbox for enterprise mode;
# - a select box for the LLM provider; and
# - a select box for the model to use, depending on the provider selected.
with st.sidebar:
    st.session_state.is_enterprise_mode = st.checkbox("Enterprise Mode")
    col1, col2 = st.columns([0.5, 0.5], gap="medium")
    with col1:
        st.session_state.llm_provider = st.selectbox("LLM provider", LLM_PROVIDERS)

    if st.session_state.llm_provider == "google-generativeai":
        with col2:
            st.session_state.model_selected = st.selectbox(
                "Gemini Models", GOOGLE_GENERATIVEAI_MODELS
            )

# Set up the header components.
st.title("Aether Chatbot")
st.subheader("Secured Chat Assistant")
st.divider()

# Display the chat history.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["response"])

# Process the prompt from the user.
if prompt := st.chat_input("Ask anything..."):

    # Add the newly input prompt to the session state.
    st.session_state.messages.append({"role": "user", "response": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = {}
    response_instance = st.chat_message("assistant")
    model_name = ""

    with response_instance:
        # The loading state.
        with st.spinner("Analyzing..."):
            llm_provider = st.session_state.llm_provider
            if llm_provider not in ("google-generativeai", "azure-openai"):
                raise LLMProviderNotFoundException()
            elif llm_provider == "google-generativeai":
                model_name = st.session_state.model_selected
            elif llm_provider == "azure-openai":
                model_name = secret_variables.azure_provider_deployment

            # Make the LLM call.
            response = invoke(
                prompt=prompt,
                llm_provider=llm_provider,
                model_name=model_name,
                is_enterprise_mode=st.session_state.is_enterprise_mode,
            )

    # Update the session state with the new response.
    with response_instance:
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "response": response})
