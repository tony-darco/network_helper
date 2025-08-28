import tempfile
import subprocess
import shutil
import os
import requests
from datetime import datetime
import json
import asyncio

from dotenv import load_dotenv
import sys

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.tools import tool
from typing import Optional, List
from pydantic import BaseModel, Field

sys.path.insert(1,"/Users/tdarco/Documents/Projects/network_helper/nobase")
import read_nobase


load_dotenv()

class ResponseFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""
    python_script: str = Field(description="The Python Script to make the api call that fulfil the request")
    followup_statement: str = Field(description="A followup statement")

def clean_script(pyscript: str) -> str:
    """
    Removes the "python" prefix from the beginning of the string

    Args:
        pyscript (str): The input string that may have a "python" prefix

    Returns:
        str: Cleaned string with "python" prefix removed
    """
    if pyscript.startswith("```python"):
        pyscript = pyscript[9:]  # Remove first 6 characters ("python")
    if pyscript.endswith("```"):
        pyscript = pyscript[:-3]
    return pyscript
    

@tool("write_script", return_direct=True)
def write_script(query:str, converstion:list):
    """Makes api calls to the meraki dashboard"""
    contxt_vec = asyncio.run(read_nobase.read_VecDB(query))
    contxt_grag = asyncio.run(read_nobase.read_graph(query))
    
    swe_prompt = ChatPromptTemplate.from_template("""
    You are a software engineer. Given the user question and the context about the question. Return a python script to make the api call to fulfil the question. Use the information about the meraki network and organization to create the script.
    here is the meraki information:
                                                  
    from dotenv import load_dotenv
    MERAKI_API_KEY= os.environ.get("MERAKI_API_KEY")
    ORGANIZATION_ID=os.environ.get("ORGANIZATION_ID")
    NETWORK_ID=os.environ.get("NETWORK_ID")

    here the context about the question: 
    {contxt_vec} 
    {contxt_grag}

    here is the request: {query}
                                                  
    Do not add any prefixes or content. Just return the script.
    """)

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_completion_tokens=1200)
    structured_llm = model.with_structured_output(ResponseFormatter, method="json_mode")  

    swe_chain = swe_prompt | model
    
    result = swe_chain.invoke({"contxt_vec":contxt_vec,"contxt_grag":contxt_grag,"query":query,
                      })
    
    print(result)

    print(result.content)

    pyscript = clean_script(result.content)
    #save python script to temp file, run temp file and grab result
    execute_script_with_conditional_save(pyscript)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
        temp_script.write(pyscript)
        temp_script_path = temp_script.name

    try:
        completed_process = subprocess.run(
            ['python3', temp_script_path],
            capture_output=True,
            text=True,
            check=False
        )
        script_output = completed_process.stdout
        script_error = completed_process.stderr

        print("Script Output:\n", script_output)
        if script_error:
            return("Script Error:\n", script_error)

        return(script_output)
    finally:
        os.remove(temp_script_path)

def execute_script_with_conditional_save(pyscript, save_condition=None, **save_kwargs):
    """
    Execute script with custom save conditions.
    
    Args:
        pyscript (str): Python script content
        save_condition (callable): Function that takes (returncode, stdout, stderr) and returns bool
        **save_kwargs: Additional arguments for saving (script_name, save_dir)
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
        temp_script.write(pyscript)
        temp_script_path = temp_script.name

    try:
        completed_process = subprocess.run(
            ['python3', temp_script_path],
            capture_output=True,
            text=True,
            check=False
        )
        
        script_output = completed_process.stdout
        script_error = completed_process.stderr
        
        print("Script Output:\n", script_output)
        if script_error:
            print("Script Error:\n", script_error)
        
        # Default save condition: successful execution (return code 0) and no stderr
        if save_condition is None:
            should_save = completed_process.returncode == 0 and not script_error
        else:
            should_save = save_condition(completed_process.returncode, script_output, script_error)
        
        if should_save:
            save_dir = save_kwargs.get('save_dir', "/Users/tdarco/Documents/Projects/network_helper/mytools")
            script_name = save_kwargs.get('script_name')
            
            os.makedirs(save_dir, exist_ok=True)
            
            if script_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                script_name = f"script_{timestamp}.py"
            elif not script_name.endswith('.py'):
                script_name += '.py'
            
            saved_script_path = os.path.join(save_dir, script_name)
            shutil.copy2(temp_script_path, saved_script_path)
            
            print(f"Script saved to: {saved_script_path}")
            return True, script_output, script_error
        
        return False, script_output, script_error
        
    finally:
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)
