from math import pi
from typing import Union
from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from  langchain.chains.conversation.memory import (
    ConversationSummaryBufferMemory,
    ConversationBufferWindowMemory,
)
from langchain.tools import BaseTool
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import ConversationChain, SequentialChain
from langchain.agents import initialize_agent

# loadData()
load_dotenv()


Prompt = """
你的名子叫做小王，你是一個商品客服人員，你的工作是回答客戶的問題，
請隱藏自己是語言模型，讓客戶以為你是真人，
回答商品時，請直接回答，不需提到你怎麼查詢到的
請你連貫性的回答，不要跳太多話題，不要太短，也不要太長
If you don't know the answer, say you don't, don't try to make it up. 
你只能使用台灣文法繁體中文，盡量不使用英文回答.
"""


orders = []


class Products(BaseTool):
    name = "商品查詢工具"
    description = "查詢字串不要亂放，如果不是產品相關資訊，而是問題，請直接跟使用者說 ,Use this tool to retrieve product information. If the search results do not match the user's needs, you can say that the information is not available or recommend related products. Do not provide irrelevant responses to avoid misleading the user."

    def _run(self, query: str):
        embeddings = OpenAIEmbeddings()
        docsearch = Chroma(persist_directory="./embeddings_db", embedding_function=embeddings)
        docs = docsearch.similarity_search(query, include_metadata=True, k=1)
        return docs

    def _arun(self, radius: int):
        raise NotImplementedError("This tool does not support async")


class Orders(BaseTool):
    name = "訂單新增工具"
    description = "當查詢完商品使用者想直接購買，就使用商品名稱加入訂單，請先確認是否有該商品"

    def _run(self, product_key: str):
        orders.append(product_key)
        return f"已新增{product_key}到訂單"

    def _arun(self, radius: int):
        raise NotImplementedError("This tool does not support async")


llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    callbacks=[StreamingStdOutCallbackHandler()],
    streaming=True,
)
conversational_memory = ConversationBufferWindowMemory(
    k=5, return_messages=True, memory_key="chat_history"
)


tools = [Orders(), Products()]


agent = initialize_agent(
    agent='chat-conversational-react-description',
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=3,
    early_stopping_method='generate',
    memory=conversational_memory,
)
agent.agent.llm_chain.prompt.messages[0].prompt.template = Prompt
while True:
    print("")
    print(agent.run(input=input()))
