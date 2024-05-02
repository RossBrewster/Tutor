import os
from dotenv import load_dotenv
from typing import List
import json
from langchain_core.agents import AgentActionMessageLog, AgentFinish
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool
from langchain.tools import BaseTool, StructuredTool, tool
from typing import Optional
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser



load_dotenv()
class QA(BaseModel):
    title: str = Field(..., description="The title of the question set")
    question: str = Field(..., description="The actual question")
    correct_answer: str = Field(..., description="The correct answer to the question")
    incorrect_answers: List[str] = Field(..., description="List of incorrect answers")
    shuffled_answers: List[str] = Field(..., description="List of answers shuffled")
class QAList(BaseModel):
    questions: List[QA] = Field(..., description="A list of multiple choice questions")
@tool("question_generator", args_schema=QAList, return_direct=False)
def make_question_set(questions: List[QA]):
    """Returns a structured multiple choice question."""
    return questions
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
llm = ChatOpenAI(api_key=api_key, temperature=0)
loader = WebBaseLoader("https://education.nationalgeographic.org/resource/coriolis-effect/")
docs = loader.load()
embeddings = OpenAIEmbeddings()
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever()
retriever_tool = create_retriever_tool(
    retriever,
    "article_retriever",
    "Searches and returns information about the article.",
)

retrieval_agent_tools = [retriever_tool]
return_agent_tools = [make_question_set]





prompt = hub.pull("hwchase17/openai-tools-agent")
return_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are very powerful assistant, That returns multiple choice questions with the correct answers noted.",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

return_llm_with_tools = llm.bind_functions(return_agent_tools)

def parse(output):
    if "function_call" not in output.additional_kwargs:
        return AgentFinish(return_values={"output": output.content}, log=output.content)
    function_call = output.additional_kwargs["function_call"]
    name = function_call["name"]
    inputs = json.loads(function_call["arguments"])
    if name == "question_generator":
        return AgentFinish(return_values=inputs, log=str(function_call))
    else:
        return AgentActionMessageLog(
            tool=name, tool_input=inputs, log="", message_log=[output]
        )

return_agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
           x["intermediate_steps"]
       ),
   }
    | return_prompt
    | return_llm_with_tools
    | parse
)
retrieval_agent = create_openai_tools_agent(llm, retrieval_agent_tools, prompt)


retrieval_agent_executor = AgentExecutor(agent=retrieval_agent, tools=retrieval_agent_tools)
return_agent_executor = AgentExecutor(tools=return_agent_tools, agent=return_agent, verbose=True)

def get_questions():
    response = retrieval_agent_executor.invoke({"input": "Write 7 multiple choice questions about the subject of the article notating the correct answer."})
    questions = response["output"]
    questions = return_agent_executor.invoke({"input": questions})
    return questions["questions"]
   