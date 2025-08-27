import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model

from nobase import read_nobase

import streamlit as st
import asyncio

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")

model = init_chat_model("gpt-4o", model_provider="openai", temperature=0)

def reset_chat():
    """
    Reset the Streamlit chat session state.
    """
    st.session_state.chat_history = []
    st.session_state.example = False # Add others if needed

if st.sidebar.button("Reset chat"):
    reset_chat()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not st.session_state.chat_history:
    st.session_state.chat_history.append(("assistant", "Hi! How can I help you?"))

for role, message in st.session_state.chat_history:
    st.chat_message(role).write(message)

user_message = st.chat_input("Type your message...")

if user_message:
    st.chat_message("user").write(user_message)
    st.session_state.chat_history.append(("user", user_message))


    MERAKI_API_KEY= os.environ.get("MERAKI_API_KEY")
    ORGANIZATION_ID=os.environ.get("ORGANIZATION_ID")
    NETWORK_ID=os.environ.get("NETWORK_ID")

    #create the python script to complete the task
    
    contxt = asyncio.run(read_nobase.read_VecDB(user_message))
    print(contxt)

    system_prompt = f"""
    You are an assistant.
    Be nice and kind in all your responses.
    """
    full_input = f"{system_prompt}\n\nUser message:\n\"\"\"{user_message}\"\"\""

    #response = model.invoke(full_input)
    response = model.invoke(full_input)
    assistant_reply = response.content

    st.chat_message("assistant").write(assistant_reply)
    st.session_state.chat_history.append(("assistant", assistant_reply))