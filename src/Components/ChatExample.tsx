// import React from 'react';

const Chat = () => {
  const messages = [
    { id: 1, sender: 'User1', text: 'Hey, how are you?' },
    { id: 2, sender: 'User2', text: 'I\'m doing great, thanks! How about you?' },
    { id: 3, sender: 'User1', text: 'I\'m good too. Just wanted to catch up.' },
    { id: 4, sender: 'User2', text: 'Sure, what\'s new with you?' },
  ];

  return (
    <div className="min-h-screen">
      <div className="max-w-lg mx-auto bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Chat</h2>
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === 'User1' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`rounded-lg p-3 ${
                  message.sender === 'User1' ? 'bg-blue-500 text-white' : 'bg-gray-200'
                }`}
              >
                {message.text}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-6">
          <input
            type="text"
            placeholder="Type your message..."
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>
  );
};

export default Chat;