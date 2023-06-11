import datetime
from math import pi
import os
from typing import Union
from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.conversation.memory import (
    ConversationSummaryBufferMemory,
    ConversationBufferWindowMemory,
)
from langchain.agents import AgentType
from langchain.tools import BaseTool
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader,TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import ConversationChain, SequentialChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents import initialize_agent
from langchain.document_loaders import PlaywrightURLLoader
from langchain.chains.summarize import load_summarize_chain
import requests
from QASystem import qaSystem
# loadData()
load_dotenv()
from opencc import OpenCC
cc = OpenCC('s2twp')
Prompt = """
你的名子叫做小王，你是一個商品客服人員，你的工作是回答客戶的問題，
不准跟別人說自己是語言模型，請讓客戶以為你是真人，
請你優先使用工具查詢資料，如果工具查不到，請不要亂回答，

若聊天紀錄上已經有之前的查詢結果，請直接回答，不使用工具查詢
If you don't know the answer, say you don't, don't try to make it up. 
每個工具會回傳另一個人幫你查到的資料，請你整理根據使用者的問題整理成中文回答，禁止直接使用工具回傳的字串回答
不准使用英文回答.根據資料整理成繁體中文回答。
若使用者想查某一個分類的產品，可以先使用 取得所有商品及分類 來查詢各個商品的分類

"""
orders = []
qa_system = qaSystem()

query_record = {}

class GetProduct(BaseTool):
    name = "商品資訊查詢"
    description = """
    查詢分類或商品是否存在優先不使用此功能，請使用者先使用 取得所有商品及分類 來查詢各個商品的分類，找不到的話再使用這個工具
    If the search not found, please tell the user that the product does not exist.
    Do not provide irrelevant responses to avoid misleading the user.
    這個工具會回傳另一個人幫你查到的資料，請你整理根據使用者的問題整理成中文回答
    不准使用英文回答.根據資料整理成繁體中文回答.若答案跟問題不相關，請先說找不到結果
    禁止直接使用工具回傳的字串回答
    """

    def _run(self, query: str):
        if query in query_record:
            return query_record[query]
        temp = (qa_system.answer(query))
        if not temp:
            return "發生錯誤，請重新輸入"
        query_record[query] = cc.convert(str(temp))
        return temp
        

    def _arun(self,query: str):
        raise NotImplementedError("This tool does not support async")


class Orders(BaseTool):
    name = "訂單新增工具"
    description = """
    若使用者需要下訂單，請使用這個工具幫使用者新增訂單
    請先叫使用者提供 配送地址、數量、聯絡電話及姓名
    不要自己亂編，請先向使用者提供
    你的input格式為 `product_key, quantity, address, phone, name`
    """

    def _run(self, input : str):
        product_key, quantity, address, phone, name = input.split(",")
        order = {
            "product_key": product_key,
            "quantity": quantity,
            "address": address,
            "phone": phone,
            "name": name,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(order)
        return f"已新增{order}到訂單"

    def _arun(self, radius: int):
        raise NotImplementedError("This tool does not support async")
    
class AllProducts(BaseTool):
    name = "取得所有商品及分類"
    description = """
    若使用者想查某一個分類的產品，可以先使用此工具 來查詢各個商品的分類，找不到的話再使用 商品資訊查詢工具

    查詢所有商品,請整理按照需要並回傳給使用者
    裡面包含了 商品名稱、商品id、分類
    所以當使用者要查 以上任意項目 都可以使用這個tool
    action_input: 請輸入"取得所有商品"
    
    """

    def _run(self,query:str):
        with open("products.json", "r",encoding="utf-8") as f:
            return f.read()

    def _arun(self):
        raise NotImplementedError("This tool does not support async")
    


