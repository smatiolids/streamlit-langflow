import streamlit as st
from pathlib import Path
import os
from langchain.schema import HumanMessage, AIMessage
import requests
from dotenv import load_dotenv
from typing import Optional
load_dotenv(override=True)

print("Started")

#################
### Functions ###
#################

# Close off the app using a password


def check_langflow_login():
    def login_form():
        """Form with widgets to collect user information"""
        with st.form("credentials"):
            st.text_input('Langflow URL', key='input_langflow_url', value=os.getenv(
                'LANGFLOW_URL'), placeholder='https://.../api/v1/run')
            st.text_input('Langflow Flow ID or Endpoint Name',
                          key='input_langflow_flow_id', value=os.getenv('LANGFLOW_FLOW_ID'))
            st.text_input('Langflow API Key', type='password',
                          key='input_langflow_api_key', value=os.getenv('LANGFLOW_API_KEY'))
            st.form_submit_button('Login', on_click=langflow_login)

    def langflow_login():
        """Checks whether a password entered by the user is correct."""
        if st.session_state['input_langflow_url'] \
            and st.session_state['input_langflow_flow_id'] \
            and st.session_state['input_langflow_api_key']:
            st.session_state['langflow_url'] = st.session_state['input_langflow_url']
            st.session_state['langflow_flow_id'] = st.session_state['input_langflow_flow_id']
            st.session_state['langflow_api_key'] = st.session_state['input_langflow_api_key']
            st.session_state['langflow_login'] = True
        else:
            st.session_state['langflow_login'] = False
    
    if st.session_state.get('langflow_url', False) \
        and st.session_state.get('langflow_flow_id', False) \
        and st.session_state.get('langflow_api_key', False):
        return True
    
    print("Show login form")
    login_form()
    return False


def logout():
    print("Logout")
    if 'langflow_api_key' in st.session_state:
        del st.session_state.langflow_api_key
    if 'langflow_flow_id' in st.session_state:
        del st.session_state.langflow_flow_id
    if 'langflow_url' in st.session_state:
        del st.session_state.langflow_url
    if 'langflow_login' in st.session_state:
        del st.session_state.langflow_login

# Function for running the flow. Almost the same code available in Langflow.


def run_flow(message: str,
             output_type: str = "chat",
             input_type: str = "chat",
             tweaks: Optional[dict] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{st.session_state.langflow_url}/{st.session_state.langflow_flow_id}?stream=false"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    headers = {"Authorization": f"Bearer {st.session_state.langflow_api_key}"}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


#############
### Login ###
#############
# Check for langflow_url/langflow_api_key
if not check_langflow_login():
    st.stop()  # Do not continue if check_langflow_login is not True.

#####################
### Session state ###
#####################

# Start with empty messages, stored in session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        AIMessage(content='Hi. How Langflow can help you?')]

############
### Main ###
############

# Write the welcome text
st.markdown(Path('./welcome.md').read_text())

# DataStax logo
with st.sidebar:
    st.image('./assets/datastax-logo-reverse_transparent-background.png')
    st.text('')

# Logout button
with st.sidebar:
    with st.form('logout'):
        st.caption(
            f"""Welcome to Streamlit Langflow! You can reset the flow by clicking on the button below.""")
        st.caption(f"""**Langflow Server:**""")
        st.text(f"""{st.session_state.get('langflow_url', False)}""")
        st.caption(f"""**Flow ID:**""")
        st.text(f"""{st.session_state.get('langflow_flow_id', False)}""")
        st.form_submit_button("Reset Flow", on_click=logout)


# Drop the Conversational Memory
with st.sidebar:
    with st.form('delete_memory'):
        st.caption("Delete Conversation")
        submitted = st.form_submit_button("Delete Conversation")
        if submitted:
            with st.spinner("Deleting Conversation"):
                st.session_state.messages = [
                    AIMessage(content='Hi. How Langflow can help you?')]


# Draw all messages, both user and agent so far (every time the app reruns)
for message in st.session_state.messages:
    st.chat_message(message.type).markdown(message.content)

# Now get a prompt from a user
if question := st.chat_input("What's up?"):
    print(f"Got question {question}")

    # Add the prompt to messages, stored in session state
    st.session_state.messages.append(HumanMessage(content=question))

    # Draw the prompt on the page
    print(f"Draw prompt")
    with st.chat_message('human'):
        st.markdown(question)

    # Get the results from Langchain
    print(f"Chat message")
    with st.chat_message('assistant'):
        # UI placeholder to start filling with agent response
        response_placeholder = st.empty()

        response = run_flow(question, output_type="chat", input_type="chat")

        print(f"Response: {response}")
        # Extract the message text from the nested JSON structure
        content = response['outputs'][0]['outputs'][0]['results']['message']['text']

        # Write the final answer without the cursor
        response_placeholder.markdown(content)

        st.session_state.messages.append(AIMessage(content=content))

with st.sidebar:
    st.caption("v1.0.0")
