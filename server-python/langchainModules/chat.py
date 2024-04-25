from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import time

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(api_key=api_key)

def chat():
    start_time = time.time()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a 7th grade tutor"),
        ("user", "{input}")
    ])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    output = chain.invoke({"input": "How do you solve for x in 2x + 3 = 7?"})
    endtime = time.time() - start_time
    return (output, endtime)