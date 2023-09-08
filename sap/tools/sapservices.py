import os
from typing import Optional
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
import chromedriver_autoinstaller

from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain.vectorstores import Chroma
from langchain.agents import tool
from sap.chat.openai import SAPChatOpenAI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

# Place where the data resides
persistDirectory = "sap/tools/btpservicesdata"

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

class VectorDBNotFoundException(Exception):
    pass
            
class Sap_btp_service_search(BaseTool):
    name = "sap-btp-service-search"
    description = "Use it to get the SAP BTP service name once you know the API or technical details."

    # Check if the DB exists
    @classmethod
    def _vectorDBExists(cls, dir: str)->bool:
        vectorDBExists = True
        folder_contents = os.listdir(dir)
        if len(folder_contents) == 0:
            vectorDBExists = False
        return vectorDBExists

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""     
        vectorDb = None
        if not Sap_btp_service_search._vectorDBExists(persistDirectory):
            raise VectorDBNotFoundException(f"No Vector DB found in {persistDirectory}.")
        # Load ChromaDB with embeddings
        vectorDb = Chroma(persist_directory=persistDirectory, embedding_function=OpenAIEmbeddings())
        relevantDocuments = vectorDb.similarity_search(query, k=4)
        result = ""
        for document in relevantDocuments:
            result += f'Service name: {document.metadata["source"].rsplit("/")[-1]}:\n{document.page_content}\n\n'
        return result
    
    async def _arun(self, query: str,  engine: str = "google", gl: str = "us", hl: str = "en", run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
    
class BTPServiceAgent:
    """ This class checks the BTP services vector database and comes back with an answer and sources."""
    def __init__(self, username: str, agentname: str, query: str) -> None:
        # User name and query
        self.username = username
        self.agentname = agentname
        self.query = query
        self.vectorDb = None
        if not Sap_btp_service_search._vectorDBExists(persistDirectory):
            raise VectorDBNotFoundException(f"No Vector DB found in {persistDirectory}.")
        # Load ChromaDB with embeddings
        self.vectorDb = Chroma(persist_directory=persistDirectory, embedding_function=OpenAIEmbeddings())        
        template = """Act like you are SAP Consultant. Your name is {agentname}. Given the following extracted parts of a long document and a question, create a final answer to {username} with references ("SOURCES"). 
        If you don't know the answer, just say that you don't know. Don't try to make up an answer.
        ALWAYS return a "SOURCES" part in your answer unless you don't know the answer.

        QUESTION: {question}
        =========
        {summaries}
        =========
        FINAL ANSWER:"""
        self.BTPPROMPT = PromptTemplate(template=template, input_variables=["summaries", "question", "username", "agentname"])

    # Check if the DB exists
    @classmethod
    def _vectorDBExists(cls, dir: str)->bool:
        vectorDBExists = True
        folder_contents = os.listdir(dir)
        if len(folder_contents) == 0:
            vectorDBExists = False
        return vectorDBExists
        
    def run(self)->str:        
        chain = load_qa_with_sources_chain(SAPChatOpenAI(temperature=0.3, model="gpt-4"), chain_type="stuff", prompt=self.BTPPROMPT, verbose=True)
        relevantDocuments = self.vectorDb.similarity_search(self.query, k=6)
        answer = chain(
                {
                    "input_documents": relevantDocuments,
                    "question": self.query,
                    "agentname": self.agentname,
                    "username": self.username,
                },
                return_only_outputs=True,
            )["output_text"]
        return answer
    
def _get_btp_service_search_tool() -> BaseTool:
    return Sap_btp_service_search()

class SearchSites():
    CALLPATTERN = "https://www.googleapis.com/customsearch/v1?key=AIzaSyB27QH7Y3GwPAlsr7PMHLaIRTHfl5dzcuo&cx=9694186ca75284163&num={num}&fileType=html&dateRestrict=y2&siteSearch='{site}'&q={query}"
    headers = {
        'Accept': 'application/json'
    }

    def __init__(self) -> None:
        self.cse = os.environ.get("GOOGLE_CSE_ID")
        self.key = os.environ.get("OPENAI_API_KEY")
        self.options = ChromeOptions()
        self.options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=self.options)

    def __del__(self):
        print("Quit Selenium driver...")
        self.driver.quit()
        print("Closed Selenium driver.")

    def searchWeb(self, query: str, n: int, class_name: str, site = '')->dict:
        url = SearchSites.CALLPATTERN.format(num=n, site=site, query=query)
        response = requests.get(url, headers=SearchSites.headers)
        if response.status_code == 200:
            try:
                search_items = response.json()["items"]
            except Exception:
                print("No information found.")
                return []
            result_data = []
            for web_page in search_items:
                site_text = self.__siteText(web_page["link"], class_name)
                result_data.append(site_text)
            return result_data
        else:
            return "I found no results so far."

    def __siteText(self, url: str, class_name: str)->dict:
        self.driver.get(url)
        try:
            el = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            print(f"Element was found: URL: {url}.")
        except Exception as e:
            print(f"Element was not found: URL: {url}.")
            #return { "text": "" }
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        r = { "text": soup.get_text() }
        return r

class Sap_search_documentation(BaseTool):
    name = "search-for-sap-documentation"
    description = "Use this tool to find information about SAP APIs or SAP documentation. Don't use for BTP services."

    # Run google search with a SAP focus
    def _run_google_search(self):
        pass

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""     
        n = 3
        s = SearchSites()
        search_results = s.searchWeb(query=query, n=n, class_name="body conbody", site = "help.sap.com")
        result = f'Use data from the best document. There are {len(search_results)} documents:\n=========\n'
        for index, document in enumerate(search_results):
            result += f'DOCUMENT {index+1}: {document["text"]}\n\n'
        return Sap_search_documentation.__smart_truncate(result)
    
    def __smart_truncate(content: str, length=8150, suffix='...'):
        if len(content) <= length:
            return content
        else:
            return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix
    
    async def _arun(self, query: str,  engine: str = "google", gl: str = "us", hl: str = "en", run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")