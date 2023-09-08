# SAP Azure OpenAI communication handler class

# Completions
# deployment_id	                        description
# text-davinci-003 (default)	        Azure OpenAI text-davinci-003 model
# code-davinci-002	                    Azure OpenAI codex model
# alephalpha	                        Aleph Alpha luminous-base model
# gpt-35-turbo	                        Azure OpenAI ChatGPT (gpt-35-turbo) model
# gpt-4	                                Azure OpenAI GPT-4 model accepting 8k maximum tokens
# gpt-4-32k	                            Azure OpenAI GPT-4 model accepting 32k maximum tokens
# bloom-7b1	BLOOM                       model hosted on AI Core supporting more parameters
# gptj-full	GPT-J                       model hosted on AI Core supporting more parameters
# gcp-text-bison-001 (Preview)	        Google text-bison@001 model for text completions

# Embeddings
# deployment_id	                        description
# text-embedding-ada-002-v2	            Azure OpenAI text-embedding-ada-002 (Version 2) model

# Two endpoints are available:
# Completions:          POST <url>/api/v1/completions
# Embeddings:           POST <url>/api/v1/embeddings


from datetime import datetime
from datetime import timedelta

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import requests
import json

# OAuth2 token
token = {
            "sapopenai": {
                "envParams": {
                    "token": "OPENAI_TOKENURL",
                    "id": "OPENAI_CLIENTID",
                    "sec": "OPENAI_CLIENTSECRET"
                },
                "token": {}
                }
        }

class Completion:
    def __init__(self):
        Completion.openai_api_client_id = ""
        Completion.openai_api_client_secret = ""
        Completion.openai_api_url = ""
        Completion.openai_api_tokenurl = ""

    def getToken(service: str) -> str:
        global token
        # -------------- Env. Variables --------------->>>
        client = BackendApplicationClient(client_id=Completion.openai_api_client_id)
        # create an OAuth2 session
        oauth = OAuth2Session(client=client)
        if token[service]['token'] == {}:
            token[service]['token'] = oauth.fetch_token(token_url=Completion.openai_api_tokenurl, client_id=Completion.openai_api_client_id, client_secret=Completion.openai_api_client_secret)    
        elif datetime.fromtimestamp(token[service]['token']['expires_at']) - datetime.now() < timedelta(seconds=60):
            token[service]['token'] = oauth.fetch_token(token_url=Completion.openai_api_tokenurl, client_id=Completion.openai_api_client_id, client_secret=Completion.openai_api_client_secret)  
        return f"{token[service]['token']['token_type']} {token[service]['token']['access_token']}"
    
    def create(**kwargs):
        Completion.openai_api_client_id = kwargs['openai_api_client_id']
        Completion.openai_api_client_secret = kwargs['openai_api_client_secret']
        Completion.openai_api_tokenurl = kwargs['openai_api_tokenurl']
        Completion.openai_api_url = kwargs['openai_api_url']
        openAiUrl = Completion.openai_api_url + '/completions'

        headers = {
            "Content-Type": "application/json",
            "Authorization": Completion.getToken("sapopenai")
        }
        completionData = {}
        for key in kwargs:
            if key in ["request_timeout", "api_type", "api_version", "openai_api_client_id",
                       "openai_api_client_secret", "openai_api_tokenurl", "openai_api_url"]:
                continue
            if key == "engine": # Needs to be mapped to deployment_id for SAP
                engine = kwargs[key]
                if engine == "":
                    engine = "text-davinci-003"                    
                completionData['deployment_id'] = engine
            else:
                completionData[key] = kwargs[key]
        jCompletionData = json.dumps(completionData)
        response = requests.post(openAiUrl, headers=headers, data=jCompletionData)
        openAiAnswer = response.json()
        return openAiAnswer

class Embedding:
    def __init__(self):
        Completion.openai_api_client_id = ""
        Completion.openai_api_client_secret = ""
        Completion.openai_api_url = ""
        Completion.openai_api_tokenurl = ""

    def getToken(service: str) -> str:
        global token
        client = BackendApplicationClient(client_id=Completion.openai_api_client_id)
        # create an OAuth2 session
        oauth = OAuth2Session(client=client)
        if token[service]['token'] == {}:
            token[service]['token'] = oauth.fetch_token(token_url=Completion.openai_api_tokenurl, client_id=Completion.openai_api_client_id, client_secret=Completion.openai_api_client_secret)    
        elif datetime.fromtimestamp(token[service]['token']['expires_at']) - datetime.now() < timedelta(seconds=60):
            token[service]['token'] = oauth.fetch_token(token_url=Completion.openai_api_tokenurl, client_id=Completion.openai_api_client_id, client_secret=Completion.openai_api_client_secret)  
        return f"{token[service]['token']['token_type']} {token[service]['token']['access_token']}"
    
    def create(**kwargs):
        Completion.openai_api_client_id = kwargs['api_client_id']
        Completion.openai_api_client_secret = kwargs['api_client_secret']
        Completion.openai_api_tokenurl = kwargs['api_token_url']
        Completion.openai_api_url = kwargs['api_url']
        openAiUrl = Completion.openai_api_url + '/embeddings'
        headers = {
            "Content-Type": "application/json",
            "Authorization": Completion.getToken("sapopenai")
        }
        completionData = {}
        for key in kwargs:
            if key == "request_timeout":
                continue
            if key == "engine": # Needs to be mapped to deployment_id for SAP
                engine = kwargs[key]
                if engine == "" or engine == "text-embedding-ada-002":
                    engine = "text-embedding-ada-002-v2"                 
                completionData['deployment_id'] = engine
            else:
                completionData[key] = kwargs[key]
        jCompletionData = json.dumps(completionData)
        response = requests.post(openAiUrl, headers=headers, data=jCompletionData)
        openAiAnswer = response.json()
        return openAiAnswer
    
class ChatCompletion:
    def __init__(self):
        Completion.openai_api_client_id = ""
        Completion.openai_api_client_secret = ""
        Completion.openai_api_url = ""
        Completion.openai_api_tokenurl = ""

    def getToken(service: str) -> str:
        global token

        client = BackendApplicationClient(client_id=Completion.openai_api_client_id)
        # create an OAuth2 session
        oauth = OAuth2Session(client=client)
        if token[service]['token'] == {}:
            token[service]['token'] = oauth.fetch_token(token_url=Completion.openai_api_tokenurl, client_id=Completion.openai_api_client_id, client_secret=Completion.openai_api_client_secret)    
        elif datetime.fromtimestamp(token[service]['token']['expires_at']) - datetime.now() < timedelta(seconds=60):
            token[service]['token'] = oauth.fetch_token(token_url=Completion.openai_api_tokenurl, client_id=Completion.openai_api_client_id, client_secret=Completion.openai_api_client_secret)  
        return f"{token[service]['token']['token_type']} {token[service]['token']['access_token']}"
    
    def create(**kwargs):
        Completion.openai_api_client_id = kwargs['openai_api_client_id']
        Completion.openai_api_client_secret = kwargs['openai_api_client_secret']
        Completion.openai_api_tokenurl = kwargs['openai_api_tokenurl']
        Completion.openai_api_url = kwargs['openai_api_url']
        openAiUrl = Completion.openai_api_url + '/completions'
        headers = {
            "Content-Type": "application/json",
            "Authorization": Completion.getToken("sapopenai")
        }
        completionData = {}
        for key in kwargs:
            if key in ["request_timeout", "api_key", "api_base", "organization", "max_tokens", "openai_api_client_id", "openai_api_client_secret", "openai_api_tokenurl", "openai_api_url"] :
                continue
            if key == "model": # Needs to be mapped to deployment_id for SAP
                engine = kwargs[key]
                if engine == "gpt-3.5-turbo":
                    engine = "gpt-35-turbo"
                if engine == "":
                    engine = "gpt-35-turbo"                    
                completionData['deployment_id'] = engine
            else:
                completionData[key] = kwargs[key]
        jCompletionData = json.dumps(completionData)
        response = requests.post(openAiUrl, headers=headers, data=jCompletionData)
        openAiAnswer = response.json()
        return openAiAnswer