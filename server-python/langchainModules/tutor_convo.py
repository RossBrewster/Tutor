import os
import fitz  # PyMuPDF
import requests
from io import BytesIO
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains.combine_documents import create_stuff_documents_chain


class Document:
    def __init__(self, text, metadata=None):
        self.page_content = text
        self.metadata = metadata if metadata is not None else {}

# Load environment variables
load_dotenv()

# Define the LLM
api_key = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(api_key=api_key)

def load_pdf_from_url(url):
    """ Fetches a PDF from a URL and returns it as a list of Document objects. """
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    pdf_stream = BytesIO(response.content)
    document = fitz.open("pdf", pdf_stream)
    docs = [Document(page.get_text("text"), metadata={"page": page.number}) for page in document]
    document.close()
    return docs


# Load the document
pdf_url = "https://www.gadoe.org/Curriculum-Instruction-and-Assessment/Assessment/Documents/Milestones/Study-Resource%20Guides/Study_Guide_GR07_2020.pdf"
docs = load_pdf_from_url(pdf_url)
# Load the embedding model
embeddings = OpenAIEmbeddings()

# Embed the documents in the vector store
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)  # Assumes `docs` are plain text
vector_store = FAISS.from_documents(documents, embeddings)

# Set up the retriever
retriever = vector_store.as_retriever()

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

# Session management for chat
class ChatSession:
    def __init__(self):
        self.chat_history = []

    def get_response(self, user_input):
        # Append user input to chat history
        self.chat_history.append(HumanMessage(content=user_input))
        
        # Retrieve the AI's response
        response = retrieval_chain.invoke({
            "chat_history": self.chat_history,
            "input": user_input
        })
        
        # Append AI response to chat history
        ai_message = response['answer']
        self.chat_history.append(AIMessage(content=ai_message))
        
        return ai_message
    

# Store sessions by user or by some unique identifier
chat_sessions = {}

def get_llm_response(user_id, user_input):
    # Get or create a chat session for the user
    if user_id not in chat_sessions:
        chat_sessions[user_id] = ChatSession()
    
    return chat_sessions[user_id].get_response(user_input)
