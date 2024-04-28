import { useEffect } from 'react';
import io, { Socket } from 'socket.io-client';

const socket: Socket = io('http://localhost:5000', { transports: ['websocket'] });

function App() {
  useEffect(() => {
    // Listen for custom events from the server
    socket.on('custom_event', (data: unknown) => {
      if (typeof data === 'string') {
        console.log('Received string data:', data);
      } else if (typeof data === 'object' && data !== null) {
        console.log('Received object data:', data);
      } else {
        console.error('Received data of unexpected type:', data);
      }
    });

    // Send a message to the server
    socket.emit('client_event', { message: 'Hello from the client!' });

    // Log connection and disconnection events
    socket.on('connect', () => {
      console.log('Connected to server');
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    return () => {
      socket.disconnect(); // Disconnect when component unmounts
    };
  }, []);

  return <div>Hello World</div>;
}

export default App;