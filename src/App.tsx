import { useState, useEffect } from 'react';
import io, { Socket } from 'socket.io-client';
import { SpinnerDotted } from 'spinners-react';
import Quiz from './Quiz';

type Message = {
  text: string;
  sender: string;
};

export type Question = {
  title: string;
  question: string;
  correct_answer: string;
  incorrectAnswers: string[];
  shuffled_answers: string[];
}


const socket: Socket = io('http://127.0.0.1:5000', { transports: ['websocket'] });

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(true);
  const [quizOn, setQuizOn] = useState(false);
  const [quizLoading, setQuizLoading] = useState(false);
  const [questions, setQuestions] = useState<Question[] | []>([]);

  useEffect(() => {
    socket.on('message_from_server', (data: { message: string }) => {
      setMessages((prev) => [...prev, { text: data.message, sender: 'server' }]);
      console.log(data);
      // Handle server message
    });

    socket.on('connect_error', (error) => {
      console.error('Failed to connect to the server:', error);
    });

    socket.on('questions_from_server', (data: {message: Question[]}) => {
      setQuestions(data.message);
      setQuizLoading(false);
      console.log(data.message);
    });

    // Clean up the socket event listeners when the component unmounts
    return () => {
      socket.off('message_from_server');
      socket.off('connect_error');
    };
  }, [questions]);

  const sendMessage = () => {
    socket.emit('message_from_client', { message: input });
    setMessages((prev) => [...prev, { text: input, sender: 'client' }]);
    // Show user's message immediately in the UI
    setInput('');
  };

  const handleDisconnect = () => {
    socket.disconnect();
    setIsConnected(false);
  };

  const handleQuestionRequest = () => {
    setQuizOn(true);
    setQuizLoading(true);
    console.log('Requesting quiz');
    socket.emit('question_request', { message: 'Send me a quiz.' });
  };


  return (
    <div className = "flex justify-center items-end w-full bg-blue-100 min-h-screen">
      <div className="p-4 bg-gray-400 rounded-2xl m-20 max-w-lg">
        {messages.length != 0 && <div className="flex flex-col space-y-2 bg-gray-800 p-4 rounded-lg">
          {messages.map((msg, index) => {
            if (msg.sender === 'client')
              return (
                <div key={index} className="max-w-xs md:max-w-md bg-green-200 p-2 rounded text-black ml-auto">
                  {msg.text}
                </div>
              );
            else
              return (
                <div key={index} className="max-w-xs md:max-w-md bg-blue-200 p-2 rounded text-black mr-auto">
                  {msg.text}
                </div>
              );
          })}
        </div>}
        <div className="flex mt-4">
          <input
            className="flex-1 border-2 border-gray-800 p-2 rounded-lg "
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold ml-4 py-2 px-4"
            onClick={sendMessage}
          >
            Send
          </button>
        </div>
        <button
          className="hidden mt-4 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          onClick={handleDisconnect}
          disabled={!isConnected}
        >
          Disconnect
        </button>
        <button
          className="bg-green-600 hover:bg-green-800 text-white font-bold py-2 px-4 rounded my-4"
          onClick={handleQuestionRequest}
          > Quiz
        </button>
      </div>
      {quizOn && quizLoading && <div className="p-4 bg-gray-400 rounded-2xl m-20 max-w-lg"><SpinnerDotted enabled={quizLoading} color="white" /></div>}
      {(questions.length != 0) && <Quiz questions={questions} />}
    </div>
    
  );
}

export default App;