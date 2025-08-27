import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os

import pandas as pd

import graphrag.api as api
from graphrag.config.load_config import load_config

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

PROJECT_DIRECTORY = "/Users/tdarco/Documents/Projects/network_helper/"

load_dotenv()

async def read_graph(query: str) -> str:
    graphrag_config = load_config(Path(PROJECT_DIRECTORY))

    entities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/entities.parquet")
    communities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/communities.parquet")
    community_reports = pd.read_parquet(
        f"{PROJECT_DIRECTORY}/output/community_reports.parquet"
    )
    relationships = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/relationships.parquet")
    text_units = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/text_units.parquet")

    response, context = await api.drift_search(
        config=graphrag_config,
        entities=entities,
        communities=communities,
        community_reports=community_reports,
        text_units=text_units,
        relationships=relationships,
        community_level=2,
        response_type="url parameters and example",
        query=query,
    )

    return(response)


async def read_VecDB(query: str) -> list[Document]:

    embeddings:OpenAIEmbeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=os.getenv("OPENAI_API_KEY"))

    vector_store = Chroma(
        collection_name="network_helper_chroma_db",
        embedding_function=embeddings,
        persist_directory="/Users/tdarco/Documents/Projects/network_helper/network_helper_chroma_db",
    )

    results: list[Document] = vector_store.similarity_search(query, k=4)

    return results

if __name__ == "__main__":
    print("Reading No Base")
    asyncio.run(read_graph("what api do i use to create an ssid"))