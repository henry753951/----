import os
from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

load_dotenv()

def loadData():
    # remove the old embeddings floder
    try:
        os.rmdir("./embeddings_db")
    except:
        pass
    loader = DirectoryLoader("./products", glob="*.txt")
    documents = loader.load()
    print(f"Load documents done, count: {len(documents)}")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_documents(texts, embeddings, metadatas=[{"source": str(i)} for i in range(len(texts))],persist_directory="./embeddings_db")
    docsearch.persist()
    return True

if __name__ == "__main__":
    loadData()