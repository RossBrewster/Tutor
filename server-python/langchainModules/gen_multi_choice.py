import os
import argparse
from dotenv import load_dotenv
from typing import List
from langchain_core.agents import AgentActionMessageLog, AgentFinish
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.pydantic_v1 import BaseModel, Field


load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

llm = ChatOpenAI(api_key=api_key, temperature=0)

class QA(BaseModel):
    title: str = Field(..., description="The title of the question set")
    question: str = Field(..., description="The actual question")
    correct_answer: str = Field(..., description="The correct answer to the question")
    incorrect_answers: List[str] = Field(..., description="List of incorrect answers")

loader = WebBaseLoader("https://education.nationalgeographic.org/resource/coriolis-effect/")
docs = loader.load()
embeddings = OpenAIEmbeddings()
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever()

query_prompt = ChatPromptTemplate.from_template("""Generate a 10 multiple choice questions based on the following context each with 1 explicitly stated correct answer and 3 incorrect answers (each question should be about the main idea of the context only):
<context>
{context}
</context>

{input}                                               
""")

output_prompt = ChatPromptTemplate.from_template("""

""")

structured_llm = llm.with_structured_output(QA)

document_chain = create_stuff_documents_chain(llm, query_prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)



class QuestionGen:
    def get_questions(user_input):
        response = retrieval_chain.invoke({"input": user_input})
        ai_questions = response
        return ai_questions
    
def get_llm_questions(user_input):
    qg = QuestionGen()
    questions = qg.get_questions(user_input)
    return questions
# langchain.chains.structured_output.base.create_structured_output_runnable

get_llm_questions("Generate a 10 multiple choice questions based on the following context each with 1 explicitly stated correct answer and 3 incorrect answers (each question should be about the main idea of the context only):")