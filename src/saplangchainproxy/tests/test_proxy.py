import unittest

class TryTesting(unittest.TestCase):
    def test_openai_chat(self):
        try:
            from saplangchainproxy.chat.openai import SAPChatOpenAI
        except Exception as e:
            print(f"Error importing: {e}")
        chat = SAPChatOpenAI(model='gpt-4', temperature=0.0)
        from langchain.chains import ConversationChain
        from langchain.memory import ConversationBufferMemory

        conversation = ConversationChain(
            llm=chat,
            memory=ConversationBufferMemory()
        )
        test_string = "Hello I'm an AI."
        test_reply = conversation.run(f"Just answer with '{test_string}'. Nothing else.")
        self.assertTrue(test_string in test_reply)

    def test_openai_llm(self):
        try:
            from saplangchainproxy.llm.openai import SAPAzureOpenAI
        except Exception as e:
            print(f"Error importing: {e}")
        llm = SAPAzureOpenAI(temperature=0.0)
        test_string = "Hello I'm an AI."
        test_reply = llm(f"Just answer with '{test_string}'. Nothing else.")
        self.assertTrue(test_string in test_reply)