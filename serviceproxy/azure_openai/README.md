# The Aether Gateway through the Azure OpenAI SDK

This is a minimalist example on how to leverage the power of the Aether engine through the [Azure OpenAI SDK](https://github.com/openai/openai-python). You can use this example to make the two-line modification to your existing agent code and get started with using Aether!

## Setup

To set up an environment for this example, follow these steps.

1. Clone this repo.

    - HTTPS
        ```bash
        git clone https://github.com/invisibl-genai/aether-cookbook.git
        ```
    - SSH
        ```bash
        git clone git@github.com:invisibl-genai/aether-cookbook.git
        ```

2. Switch to the `serviceproxy/azure_openai/` directory.

    ```bash
    cd serviceproxy/azure_openai/
    ```

3. (Optional:) Set up a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

    ```bash
    python3 -m venv .venv
    ```
    
    Once this is done, activate the environment.
    - On Posix systems
        ```bash
        source .venv/bin/activate
        ```
    - On Windows systems
        ```powershell
        .venv\Scripts\activate
        ```
    
    *N.B.*: To deactivate the virtual environment when you're done, simply run `deactivate`, regardless of your operating system.

4. Install the requirements for the example.

    ```bash
    python3 -m pip install -r requirements.txt
    ```

5. Set up the required environment variables. We recommend storing these in a `.env` file within this folder. The contents of that file will look like this. (The example will automatically take note of any `.env` file within this folder and load its contents into the environment variables.)

    ```bash
    AETHER_API_KEY="your-aether-api-key"
    AETHER_PROXY_ENDPOINT="your-aether-proxy-endpoint"
    AZURE_PROVIDER_MODEL="your-azure-deployment-name"
    ```

6. Finally, run the example script.

    ```bash
    python3 run.py
    ```
