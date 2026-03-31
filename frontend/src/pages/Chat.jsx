import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Chat.css';

export default function Chat() {
  const { teamId } = useParams();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [connected, setConnected] = useState(false);
  const socketRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/chat/${teamId}/`;
    socketRef.current = new WebSocket(wsUrl);

    socketRef.current.onopen = () => {
      setConnected(true);
      console.log('Connected to chat');
    };

    socketRef.current.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setMessages((prev) => [...prev, data]);
    };

    socketRef.current.onclose = () => {
      setConnected(false);
      console.log('Disconnected from chat');
    };

    return () => {
      socketRef.current?.close();
    };
  }, [teamId]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim() || !connected) return;

    socketRef.current.send(JSON.stringify({
      message: input,
      username: user.username
    }));
    setInput('');
  };

  return (
    <div className="chat-container animate-fade-in">
      <div className="chat-header">
        <div className="chat-status">
          <div className={`status-dot ${connected ? 'online' : 'offline'}`} />
          <h2>Team Chat</h2>
        </div>
        <p className="chat-subtitle">Real-time collaboration for your project</p>
      </div>

      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`message-wrapper ${m.username === user.username ? 'sent' : 'received'}`}>
            <div className="message-info">
              <span className="message-user">{m.username === user.username ? 'You' : m.username}</span>
            </div>
            <div className="message-bubble">
              {m.message}
            </div>
          </div>
        ))}
        <div ref={scrollRef} />
      </div>

      <form onSubmit={handleSend} className="chat-input-area">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={connected ? "Type a message..." : "Connecting to chat..."}
          disabled={!connected}
        />
        <button type="submit" className="btn btn-primary" disabled={!connected || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
