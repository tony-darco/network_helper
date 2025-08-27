import asyncio
from dotenv import load_dotenv
import os

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from langchain_core.documents import Document

load_dotenv()

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
    asyncio.run(read_VecDB("what api do i use to create an ssid"))