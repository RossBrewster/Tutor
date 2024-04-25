import { ChatOpenAI } from "@langchain/openai";
import dotenv from "dotenv";

dotenv.config();

export default async function runChaining(){
    const chatModel = new ChatOpenAI({apiKey: process.env.OPENAI_API_KEY });
    const response = await chatModel.invoke("What is LangSmith");
    // console.log(response.content);
    return response.content;
}


