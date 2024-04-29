import { useState, useEffect } from 'react';
import io, { Socket } from 'socket.io-client';

type Message = {
  text: string;
  sender: string;
};

const socket: Socket = io('http://127.0.0.1:5000', { transports: ['websocket'] });

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    socket.on('message_from_server', (data: { message: string }) => {
      setMessages((prev) => [...prev, { text: data.message, sender: 'server' }]);
      console.log(data);
      // Handle server message
    });

    socket.on('connect_error', (error) => {
      console.error('Failed to connect to the server:', error);
    });

    // Clean up the socket event listeners when the component unmounts
    return () => {
      socket.off('message_from_server');
      socket.off('connect_error');
    };
  }, []);

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

  return (
    <div className="p-4">
      <div className="flex flex-col space-y-2">
        {messages.map((msg, index) => {
          if (msg.sender === 'client')
            return (
              <div key={index} className="max-w-xs md:max-w-md bg-green-200 p-2 rounded">
                {msg.text}
              </div>
            );
          else
            return (
              <div key={index} className="max-w-xs md:max-w-md bg-blue-200 p-2 rounded">
                {msg.text}
              </div>
            );
        })}
      </div>
      <div className="flex mt-4">
        <input
          className="flex-1 border-2 border-gray-300 p-2 rounded-l"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-l"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
      <button
        className="mt-4 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
        onClick={handleDisconnect}
        disabled={!isConnected}
      >
        Disconnect
      </button>
    </div>
  );
}

export default App;