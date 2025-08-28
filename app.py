import os
import asyncio
import time
import streamlit as st
import json
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from nobase import read_nobase
import mytools

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

def clean_json(archive_result: str) -> str:
    """
    Removes code block markers, backslashes, newlines, and quotes from JSON string

    Args:
        archive_result (str): The input string that may have formatting artifacts

    Returns:
        str: Cleaned string with unwanted characters removed
    """
    # Remove code block markers
    if archive_result.startswith("```json"):
        archive_result = archive_result[7:]  # Remove "```json"
    if archive_result.endswith("```"):
        archive_result = archive_result[:-3]
    
    # Remove backslashes, newlines, and quotes
    archive_result = archive_result.replace("\\", "")
    archive_result = archive_result.replace("\n", "")
    archive_result = archive_result.replace('"{', "{")
    archive_result = archive_result.replace('}"', "}")
    
    return archive_result

async def build_contxt(output:str):
    network_archive = ""
    with open("/Users/tdarco/Documents/Projects/network_helper/archive.json", "r") as archive_file:
            network_archive = json.load(archive_file)

    archive_prompt = ChatPromptTemplate.from_template("""You are going to act like an archivist. Given this following network information return a summary of the data. The archive entry should include important details about the network. This can could include the device on the network, their manufacturer, their names, the device meraki network id, their mac addresses. There is an existing archive, you are to return an update to the archive. The Archive is empty or doesn't include a device,network,ssid etc. make a new entry.
                                                      
    Here is the orginal Archive: {network_archive}
    Here is the Network Data: {network_data}
        
    Keep the entry concise. 
    Do not add any prefixes or content. Just return the json.
        """)

    archive_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    archive_chain = archive_prompt | archive_model

    archive_result = archive_chain.invoke({"network_archive":network_archive,"network_data":output})
    archive_content = clean_json(archive_result.content)
    print("\n\n\n",archive_content,"\n\n\n")
    network_data = json.loads(archive_content)

    with open("/Users/tdarco/Documents/Projects/network_helper/archive.json", "w") as archive_file:
        json.dump(network_data, archive_file, indent=2)


if user_message:
    st.chat_message("user").write(user_message)
    st.session_state.chat_history.append(("user", user_message))

    network_archive = ""
    with open("/Users/tdarco/Documents/Projects/network_helper/archive.json", "r") as archive_file:
            network_archive = json.load(archive_file)
            network_archive = json.dumps(network_archive)

    MERAKI_API_KEY= os.environ.get("MERAKI_API_KEY")
    ORGANIZATION_ID=os.environ.get("ORGANIZATION_ID")
    NETWORK_ID=os.environ.get("NETWORK_ID")

    #create the python script to complete the task
    
    contxt = asyncio.run(read_nobase.read_VecDB(user_message))
    #print(contxt)

    #response = model.invoke(full_input)
    
    tool_model = model.bind_tools(tools=mytools.__all__)

    messages = [
    *[
        {"role": role, "content": msg} for role, msg in st.session_state.chat_history
    ]
    ]

    ai_msg = tool_model.invoke(messages)
    messages.append(ai_msg)

    for tool_call in ai_msg.tool_calls:
        selected_tool = {str(n.name):n for n in mytools.__all__}[tool_call["name"]]
        #selected_tool = {"NetworkCreate-tool": post_network,}[tool_call["name"]]
        tool_msg = selected_tool.invoke(tool_call)
        messages.append(tool_msg)

    system_prompt = """
        You are an Network assistant for Tony.
        Be nice and kind in all your responses.
        """
    full_input = f"""{system_prompt}

        Here is are the pervious chats:{network_archive}

        Here is some information about the network:{messages}
        
        User message:{user_message}
        """

    response = model.invoke(full_input)
    assistant_reply = response.content
    #print("done", assistant_reply, response ,time.time())

    st.chat_message("assistant").write(assistant_reply)

    asyncio.run(build_contxt(assistant_reply))

    st.session_state.chat_history.append(("assistant", assistant_reply))