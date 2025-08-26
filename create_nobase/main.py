from pathlib import Path

import graphrag.api as api
from graphrag.config.load_config import load_config
from graphrag.index.typing.pipeline_run_result import PipelineRunResult



import pandas as pd

PROJECT_DIRECTORY = "/Users/tdarco/Documents/Projects/network_helper/"

import asyncio

async def create_index():

    graphrag_config = load_config(Path(PROJECT_DIRECTORY))
    index_result: list[PipelineRunResult] = await api.build_index(config=graphrag_config)

    return(index_result)

async def create_vecDB():
    #open input dir

    #chuck docs
    #store vec




if __name__ == "__main__":
    print("creating nobase:")

    #pull files about the api

    #init verb creation
        #pull api link
        #api description
    asyncio.run(create_index())

    print("Done with nobase")
