from pull_topology import main as topology_data

import json
import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import FewShotChatMessagePromptTemplate
from langchain_ollama.llms import OllamaLLM



load_dotenv()

network_id = os.environ.get("NETWORK_ID")
org_id = os.environ.get("ORGANIZATION_ID")
MERAKI_API_KEY = os.environ.get("MERAKI_API_KEY")

example_file = os.environ.get("EXAMPLE_FILE")
summary_file = os.environ.get("SUMMARY_FILE")

neo4j_uri = os.environ["NEO4J_URI"]
neo4j_username = os.environ["NEO4J_USERNAME"]
neo4j_password = os.environ["NEO4J_PASSWORD"]


model = OllamaLLM(model="qwen2.5-coder:32b", base_url="http://192.168.1.109:11434")

def summarize_topo() -> str:
    try:
        with open(example_file, "r") as f:
            fixture_example = f.read()
            fixture_example = json.loads(fixture_example)
    except Exception as e:
        print(e)
    
    fixture_prompt = fixture_example["prompt"]
    fixture_output = fixture_example["output"]
    example_summary = [
        {"input" : fixture_prompt, "output" : fixture_output},
    ]
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    few_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=example_summary,
    )

    sum_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                            """Given the Network data return a summary of the data. The Summary should include details on the manufacturer, the name of the device, its mac address. The summary should detail which node the device is connected and which devices are connected to the device. Keep the summary concise. Network Data: {data}""",
                    ),
                    few_prompt,
                ]
            )

    chain = sum_prompt | model
    response = chain.invoke({"data": topology_data()})

    return(response)

def store_topo() -> None:
    summary:str = summarize_topo()

    try:
        with open(summary_file, "w") as sum_file:
            sum_file.write(summary)
    except Exception as e:
        print(e)

def retrieve_topo() -> str:
    summary:str = ""

    try:
        with open(summary_file, "r+") as sum_file:
            summary = sum_file.read()
    except Exception as e:
        print(e)

    return(summary)

