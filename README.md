# SAP Langchain Proxy to work with AI models at SAP 
# OpenAI SAP BTP Proxy

The OpenAI SAP BTP Proxy is a Python library that provides a proxy to connect to OpenAI services through SAP Business Technology Platform (BTP) with OAuth2 authentication. It abstracts interactions with various OpenAI models for tasks such as generating completions, working with embeddings, and using chat-based language models.

## Features

- **Completions**: Interact with OpenAI models for text completions.
- **Embeddings**: Work with text embeddings using OpenAI models.
- **Chat Completions**: Utilize chat-based language models for conversational applications.

## Usage

To use the library, you need to provide the necessary configuration for OAuth2 authentication and OpenAI endpoints. Below is an example of how to set up and use the library:

```python
# Configure OAuth2 and OpenAI endpoints
oauth_config = {
    "openai_api_client_id": "YOUR_CLIENT_ID",
    "openai_api_client_secret": "YOUR_CLIENT_SECRET",
    "openai_api_tokenurl": "OPENAI_TOKEN_URL",
    "openai_api_url": "OPENAI_API_URL"
}
```
It's recommended, though to provide the parameters as environment variables

```
OPENAI_CLIENTID
OPENAI_CLIENTSECRET
OPENAI_APIURL
OPENAI_TOKENURL
```

## Example code
Use below examples for LLM or Chat models in langchain
```python
from saplangchainproxy.chat import SAPChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
chat = SAPChatOpenAI(model='gpt-4', temperature=0.0)
conversation = ConversationChain(
    llm=chat,
    memory=ConversationBufferMemory()
)
test_string = "Hello I'm an AI."
test_reply = conversation.run(f"Just answer with '{test_string}'. Nothing else.")
print(f"AI response is: {test_reply}")

from saplangchainproxy.llm import SAPAzureOpenAI
llm = SAPAzureOpenAI(temperature=0.0)
test_string = "Hello I'm an AI."
test_reply = llm(f"Just answer with '{test_string}'. Nothing else.")
print(f"AI response is: {test_reply}")
```
## License
This library is licensed under the MIT License. See the LICENSE file for details.