import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import dotenv from "dotenv";

dotenv.config();


export default async function runLangChain(){
    const chatModel = new ChatOpenAI({apiKey: process.env.OPENAI_API_KEY });
    const prompt = ChatPromptTemplate.fromMessages([
      ["system", "You are a world class technical documentation writer."],
      ["user", "{input}"],
    ]);
    const chain = prompt.pipe(chatModel);
    await chain.invoke({
        input: "what are the main features of LangSmith?",
      });
    
    return chain
}
