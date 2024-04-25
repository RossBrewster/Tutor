import express from 'express';
import dotenv from 'dotenv';
import runLangChain from './langChainModules/langChain';
import runChaining from './langChainModules/langChain';

dotenv.config();

const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/langchain', async (req, res) => {
  try {
    const response = await runLangChain();
    res.json(response);
  } catch (error) {
    res.status(500).json(error);
  }
});

app.get('/chaining', async (req, res) => {
  try {
    const response = await runChaining();
    res.json(response);
  } catch (error) {
    res.status(500).json(error);
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});