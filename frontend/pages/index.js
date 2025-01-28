import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/greet', { name });
      setMessage(response.data.message);
    } catch (error) {
      console.error('Error:', error);
      setMessage('Error occurred while fetching the greeting');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6 text-center">Greeting App</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Enter your name:
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Get Greeting
          </button>
        </form>
        {message && (
          <div className="mt-4 p-4 bg-green-100 rounded-md">
            <p className="text-green-700">{message}</p>
          </div>
        )}
      </div>
    </div>
  );
}
