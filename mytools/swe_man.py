contxt = ""
user_message = ""

swe_prompt = f"""
    You are a software engineer. Given the user question and the context about the question. Return a python script to make the api call to for fill the question. Use the information about the meraki network and organization to create the script.
    here is the meraki information:

    MERAKI_API_KEY= os.environ.get("MERAKI_API_KEY")
    ORGANIZATION_ID=os.environ.get("ORGANIZATION_ID")
    NETWORK_ID=os.environ.get("NETWORK_ID")

    here the context about the question: {contxt}

    here is the request: {user_message}
    """