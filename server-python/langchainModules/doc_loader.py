from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain




# load the environment variables
load_dotenv()

# define the LLM
api_key = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(api_key=api_key)


# load the document
loader = WebBaseLoader("https://docs.smith.langchain.com/user_guide")

docs = loader.load()

# load the embedding model
embeddings = OpenAIEmbeddings()


# embed the documents in the vector store
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)


# Create the chain
prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")
document_chain = create_stuff_documents_chain(llm, prompt)


# Set up the retrieval chain
retriever = vector.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# get the response
response = retrieval_chain.invoke({"input": "How can langsmith help with testing?"})
print(response["answer"])
