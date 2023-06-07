from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from load import loadData
from langchain.chains import ConversationalRetrievalChain,RetrievalQAWithSourcesChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


# loadData()
load_dotenv()


class qaSystem:
    system_template = """
      Use the following context to answer the user's question.
      Hide the fact that you are a language model, so that customers think you are a real person.
      You have to pretend that you are a product customer service person and answer customers' questions. If you don't know the answer, just say you don't, don't make it up. And answer the Taiwanese in Traditional Chinese. 
      -----------
      {context}
      """
    messages : list = None
    prompt : PromptTemplate = None
    llm : LLMChain = None
    embeddings : OpenAIEmbeddings = None
    docsearch : Chroma = None
    retriever : Chroma = None
    qa : ConversationalRetrievalChain = None

    def __init__(self):
        self.messages = [
            SystemMessagePromptTemplate.from_template(self.system_template),
            HumanMessagePromptTemplate.from_template('{question}'),
        ]

        self.prompt = ChatPromptTemplate.from_messages(self.messages)

        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", callbacks=[StreamingStdOutCallbackHandler()],streaming=True,)
        self.embeddings = OpenAIEmbeddings()
        self.docsearch = Chroma(persist_directory="./embeddings_db", embedding_function=self.embeddings)
        self.retriever = self.docsearch.as_retriever()
        # self.retriever.search_kwargs['distance_metric'] = 'cos'
        # self.retriever.search_kwargs['fetch_k'] = 100
        # self.retriever.search_kwargs['maximal_marginal_relevance'] = True
        # self.retriever.search_kwargs['k'] = 10
        self.qa = RetrievalQAWithSourcesChain.from_chain_type(self.llm, chain_type="stuff", retriever=self.retriever)

    def answer(self, question):
      # color print the question
      print(f"\033[1;32;40m{question}\033[0m")
      print("\033[1;32;35mChatting with the QA model... \033[0m")
      result = self.qa({'question': "等等使用成繁體中文回答 "+question,'chat_history': []})
    #   print(f"\033[1;32;38m{result}\033[0m")
      return result


if __name__ == "__main__":
   qa = qaSystem()
   qa.answer("iphone 13 的詳細資訊")