import unittest

class TestProxyOpenAIStream(unittest.TestCase):

    def test_openai_stream(self):
        try:
            from saplangchainproxy.llm import SAPAzureOpenAI
            from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
        except Exception as e:
            print(f"Error importing: {e}")
            self.assertTrue(False)

        llm = SAPAzureOpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0.0)
        resp = llm("Write me a song about sparkling water.")
        print(resp)

unittest.main()