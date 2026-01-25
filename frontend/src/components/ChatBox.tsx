import { useState, useRef, useEffect } from 'react';
import './ChatBox.css';

interface ChatBoxProps {
  onSpeakingStateChange: (isSpeaking: boolean) => void;
}

export default function ChatBox({ onSpeakingStateChange }: ChatBoxProps) {
  const [messages, setMessages] = useState<{role: string, text: string}[]>([
    { role: 'leo', text: "Hi! I'm Leo! How is your tummy feeling?" }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Notify parent when typing state changes
  useEffect(() => {
    onSpeakingStateChange(isTyping);
  }, [isTyping, onSpeakingStateChange]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');
    setIsTyping(true); // <--- Triggers Lion Mouth Open

    try {
      const response = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: "demo_child",
          message: userMsg,
          age: 7,
          condition: "diabetes" 
        })
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let leoReply = "";

      setMessages(prev => [...prev, { role: 'leo', text: "..." }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.trim() === '') continue;
          if (line.startsWith('data: ')) {
            const text = line.replace('data: ', '').trim();
            if (text === "[DONE]") break;
            
            try {
              const parsed = JSON.parse(text); 
              leoReply += parsed; 
            } catch (e) {
              leoReply += text.replace(/^"|"$/g, '');
            }

            setMessages(prev => {
              const newMsg = [...prev];
              newMsg[newMsg.length - 1].text = leoReply;
              return newMsg;
            });
          }
        }
      }
    } catch (e) {
      console.error("Chat Error", e);
    } finally {
      setIsTyping(false); // <--- Triggers Lion Mouth Close
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-list">
        {messages.map((m, i) => (
          <div key={i} className={`message-bubble ${m.role}`}>
            {m.text}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Talk to Leo..."
          disabled={isTyping}
        />
        <button onClick={sendMessage} disabled={isTyping}>
          {isTyping ? '🦁' : '➤'}
        </button>
      </div>
    </div>
  );
}