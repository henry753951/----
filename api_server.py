import logging
from typing import Union

from fastapi import FastAPI
import datetime
from math import pi
import os
from typing import Union
from dotenv import load_dotenv
from langchain import PALChain, PromptTemplate
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
from load import loadData
from pydantic import BaseModel

from main import AllProducts, GetProduct, Prompt
load_dotenv()
# loadData()


class question(BaseModel):
    question: str


from opencc import OpenCC
cc = OpenCC('s2twp')

app = FastAPI()
logger = logging.getLogger("gunicorn.error")

class LLM:
    def __init__(self,temperature:float=0.3,model_name:str="gpt-3.5-turbo",verbose:bool=True):
        self.llm = ChatOpenAI(
            model_name=model_name,
            callbacks=[StreamingStdOutCallbackHandler()],
            streaming=True,
            temperature=temperature,
        )
        self.pal_chain = PALChain.from_math_prompt(self.llm, verbose=True)
        conversational_memory = ConversationBufferWindowMemory(
            k=5, return_messages=True, memory_key="chat_history"
        )
        self.tools = [GetProduct(),AllProducts()]
        self.agent = initialize_agent(
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            max_iterations=3,
            early_stopping_method='generate',
            memory=conversational_memory,
            handle_parsing_errors="final answer Just return the error message",
        )
        self.agent.agent.llm_chain.prompt.messages[0].prompt.template = Prompt


llmSys = LLM()

@app.get("/reload_data")
def reload_data():
    loadData()
    return {"msg": "success"}


@app.post("/pal")
def pal(question: question):
    try:
        return llmSys.pal_chain.run(question.question)
    except:
        return "請在試一次"


@app.post("/chat_withProduct")
def chat_withProduct(question: question):
    try:
        return llmSys.agent.run(input=question.question)
    except:
        return "請在試一次"

@app.post("/addProduct")
def addProduct(data: dict):
    with open("./products.json","r",encoding="utf-8",) as f:
        products = eval(f.read())
    products.append({
        "id": str(len(products)+1),
        "name": data["name"],
        "category": data["category"],
        "price": int(data["price"]),
        "fileName": F"{str(len(products)+1)}.txt",
    })
    with open("./products.json","w",encoding="utf-8",) as f:
        f.write(str(products))

    with open("./products/"+str(len(products))+".txt", "w",encoding="utf-8") as f:
        prefix = F"""
        Product Name: {data["name"]}
        Category: {data["category"]}
        Price: {data["price"]}\n\n
        """
        f.write(prefix+data["description"])
    print(F"Add Product: {data}")
    return {"msg": "success"}

@app.post("/updateProduct")
def updateProduct(data: dict):
    # update product in products.json
    with open("./products.json","r",encoding="utf-8",) as f:
        products = eval(f.read())
    for i in range(len(products)):
        if products[i]["id"] == data["id"]:
            products[i]["name"] = data["name"]
            products[i]["category"] = data["category"]
            products[i]["price"] = int(data["price"])
            break
    with open("./products.json","w",encoding="utf-8",) as f:
        f.write(str(products))
    # update product file
    with open("./products/"+data["fileName"], "w",encoding="utf-8") as f:
        prefix = F"""
        Product Name: {data["name"]}
        Category: {data["category"]}
        Price: {data["price"]}\n\n
        """
        f.write(prefix+data["description"])
    print(F"Update Product: {data}")
    return {"msg": "success"}

@app.get("/getProduct/{id}")
def getProduct(id: str):
    # get decsription from product file, filename is productname in json
    with open("./products.json","r",encoding="utf-8",) as f:
        products = eval(f.read())
    for product in products:
        if product["id"] == id:
            with open("./products/"+product["fileName"], "r") as f:
                description = f.read()
            return {"msg": description}
    return {"msg": "error"}

@app.get("/getProducts")
def getProducts():
    with open("./products.json","r",encoding="utf-8",) as f:
        products = eval(f.read())
    return {"msg": products}

@app.get("/removeProduct/{id}")
def removeProduct(id: str):
    # remove product from products.json
    with open("./products.json","r",encoding="utf-8",) as f:
        products = eval(f.read())
    for i in range(len(products)):
        if products[i]["id"] == id:
            del products[i]
            break
    with open("./products/products.json", "w") as f:
        f.write(str(products))
    # remove product file
    os.remove("./products/"+id+".txt")
    print(F"Remove Product: {id}")
    return {"msg": "success"}




@app.post("/chat_withProduct")
def changeConfig(data: dict):
    # check if the data is valid
    if "temperature" not in data or "model_name" not in data:
        return {"msg": "error"}
    global llmSys
    llmSys = LLM(temperature=data["temperature"],model_name=data["model_name"])
    print(F"Change Config: {data}")
    return {"msg": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000,reload=True)