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
from langchain.chains import  ConversationalRetrievalChain
from langchain.prompts.chat import (
  ChatPromptTemplate,
  SystemMessagePromptTemplate,
  HumanMessagePromptTemplate
)


# loadData()
load_dotenv()


system_template = """
Use the following context to answer the user's question.
Hide the fact that you are a language model, so that customers think you are a real person.
You have to pretend that you are a product customer service person and answer customers' questions. If you don't know the answer, just say you don't, don't make it up. And answer the Taiwanese in Traditional Chinese. 
-----------
{context}
"""

messages = [
  SystemMessagePromptTemplate.from_template(system_template),
  HumanMessagePromptTemplate.from_template('{question}')
]
prompt = ChatPromptTemplate.from_messages(messages)

llm = ChatOpenAI(model_name="gpt-3.5-turbo",callbacks=[StreamingStdOutCallbackHandler()])
embeddings = OpenAIEmbeddings()
docsearch = Chroma(persist_directory="./embeddings_db", embedding_function=embeddings)
retriever = docsearch.as_retriever()

qa = ConversationalRetrievalChain.from_llm(llm, retriever, condense_question_prompt=prompt)


questions = [
    '我想買一台iphone14',
]


chat_history = []
print("Chatting with the model...")
for question in questions:  
    result = qa({'question': question, 'chat_history': chat_history})
    chat_history.append((question, result['answer']))
    print(result['answer'])




