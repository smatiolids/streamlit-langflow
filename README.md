# Streamlit with Langflow

This is a simple Streamlit app that uses Langflow flows to run a conversational flow.

## Installation

```bash
poetry install
```

## Setup

If want to set default values for the fields, set the environment variables in the `.env` file. Otherwise, you can fill the values in the login form.

Copy the `.env_sample` file to `.env` and set the variables.

```bash
cp .env_sample .env
```

### Where do you get the values for the environment variables?

LANGFLOW_URL: On Langflow, go to the flow you want to use, click on the "API" button, and check the `curl` host. Copy it until the `api/v1/run` part.

LANGFLOW_FLOW_ID: From the same URL, copy the part after `api/v1/run/` until the `?stream=false` part. It is a UUID. You can also set a `enpoint name` in the settings of the flow.

LANGFLOW_API_KEY: On the API tab,  click on `Generate Token`. Copy the token.

## Run

```bash
poetry run streamlit run app.py
```


