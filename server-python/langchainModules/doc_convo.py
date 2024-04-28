from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains.combine_documents import create_stuff_documents_chain

# load the environment variables
load_dotenv()

# define the LLM
api_key = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(api_key=api_key)

# load the document
loader = WebBaseLoader("https://flask-socketio.readthedocs.io/en/latest/")
docs = loader.load()

# load the embedding model
embeddings = OpenAIEmbeddings()

# embed the documents in the vector store
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)

# Set up the retriever
retriever = vector.as_retriever()

# Set up the prompt templates
query_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("user", "Given the above conversation, generate a search query to look up to get information relevant to the conversation")
])

response_prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's questions based on the below context:\n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])

# Set up the chains
retriever_chain = create_history_aware_retriever(llm, retriever, query_prompt)
document_chain = create_stuff_documents_chain(llm, response_prompt)
retrieval_chain = create_retrieval_chain(retriever_chain, document_chain)

# Initialize chat history
chat_history = []

print("Welcome to the LangChain conversational AI! Type 'quit' to exit.")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == 'quit':
        print("Goodbye!")
        break
    
    chat_history.append(HumanMessage(content=user_input))
    
    response = retrieval_chain.invoke({
        "chat_history": chat_history,
        "input": user_input
    })
    
    print(f"AI: {response['answer']}")
    chat_history.append(AIMessage(content=response['answer']))