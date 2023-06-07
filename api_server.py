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
load_dotenv()
# loadData()


class question(BaseModel):
    question: str


from opencc import OpenCC
cc = OpenCC('s2twp')

app = FastAPI()
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    callbacks=[StreamingStdOutCallbackHandler()],
    streaming=True,
)
pal_chain = PALChain.from_math_prompt(llm, verbose=True)


@app.get("/reload_data")
def reload_data():
    loadData()
    return {"msg": "success"}


@app.post("/pal")
def pal(question: question):
    return {"msg": pal_chain.run(question.question)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_server:app", host="0.0.0.0", port=8000,reload=True)