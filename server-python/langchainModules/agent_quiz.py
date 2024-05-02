from dotenv import load_dotenv
import os
import argparse
from typing import List
import json
from langchain_core.agents import AgentActionMessageLog, AgentFinish
from langchain_openai import ChatOpenAI
from langchain.agents import tool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from gen_multi_choice import get_llm_questions



load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

llm = ChatOpenAI(api_key=api_key, temperature=0)

class MultipleChoiceQuestion(BaseModel):
    title: str = Field(..., description="The title of the question set")
    question: str = Field(..., description="The actual question")
    correct_answer: str = Field(..., description="The correct answer to the question")
    incorrect_answers: List[str] = Field(..., description="List of incorrect answers")

    def __str__(self):
        return f"Title: {self.title}\nQuestion: {self.question}\nCorrect Answer: {self.correct_answer}\nIncorrect Answers: {self.incorrect_answers}"

@tool
def make_question_set(questions: List[MultipleChoiceQuestion]):
    """Returns a structured multiple choice question."""
    return questions

tools = [make_question_set]

class Response(BaseModel):
    """Final response to returning questions."""

    questions: List[MultipleChoiceQuestion] = Field(description="List of multiple choice questions.") 


def parse(output):
    if "function_call" not in output.additional_kwargs:
        return AgentFinish(return_values={"output": output.content}, log=output.content)
    function_call = output.additional_kwargs["function_call"]
    name = function_call["name"]
    inputs = json.loads(function_call["arguments"])
    if name == "Response":
        output = AgentFinish(return_values=inputs, log=str(function_call))
        return output["return_values"]
    else:
        return AgentActionMessageLog(
            tool=name, tool_input=inputs, log="", message_log=[output]
        )


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that serves quizzes to students by calling the function to return a set of multiple choice questions. The function takes a list of multiple choice questions as input. The questions should be about the main idea of the context only. The function should return a structured multiple choice question."),
        ("user", "{input}"),
        
    ]
)
llm_with_tools = llm.bind_functions([make_question_set, Response])
agent = (
    {
        "input": lambda x: x["input"],
        # Format agent scratchpad from intermediate steps
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | parse
)
agent_executor = AgentExecutor(tools=[make_question_set], agent=agent, verbose=True)


class QuestionReturn:
    def return_questions(questions):
        response = agent_executor.invoke(
            {"input": questions}, return_only_outputs=True
        )
        returned_questions = response["inputs"]
        return returned_questions


def return_llm_questions(input):
    question_return = QuestionReturn()
    qa = agent_executor.invoke(
        {"input": {input}},
        return_only_outputs=True,
    )

