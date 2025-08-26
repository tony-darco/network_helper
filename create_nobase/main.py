from pathlib import Path
import asyncio

from dotenv import load_dotenv

import graphrag.api as api
from graphrag.config.load_config import load_config
from graphrag.index.typing.pipeline_run_result import PipelineRunResult

import json
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveJsonSplitter

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PROJECT_DIRECTORY = "/Users/tdarco/Documents/Projects/network_helper/"

async def create_index():

    graphrag_config = load_config(Path(PROJECT_DIRECTORY))
    index_result: list[PipelineRunResult] = await api.build_index(config=graphrag_config)

    return(index_result)

async def create_vecDB():
    #open input dir
    
    #chuck docs
    #store vec

    loader: JSONLoader = JSONLoader(
        file_path="/Users/tdarco/Documents/Projects/network_helper/input/meraki_api_doc.txt",
        jq_schema=".",
        text_content=False,
    )

    docs:list[Document] = loader.load()

    splitter:RecursiveJsonSplitter = RecursiveJsonSplitter(max_chunk_size=1200)
    json_chunks = []
    for doc in docs:
        # Convert doc.page_content to JSON
        json_data:json = json.loads(doc.page_content)
        json_chunks:list[Document] = splitter.create_documents(texts=[json_data])

    embeddings:OpenAIEmbeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    Chroma(
        collection_name="network_helper_chroma_db",
        embedding_function=embeddings,
        persist_directory="/Users/tdarco/Documents/Projects/network_helper/network_helper_chroma_db",  # Where to save data locally, remove if not necessary
    ).add_documents(documents=json_chunks)


if __name__ == "__main__":
    print("creating nobase:")

    asyncio.run(create_index())
    asyncio.run(create_vecDB())

    print("Done with nobase")
