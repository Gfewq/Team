import { useState, useRef, useEffect } from 'react';
import './ChatBox.css';
import { MoodEntry } from './MoodTracker';

interface Message {
  role: string;
  text: string;
  timestamp?: Date;
}

interface ChatBoxProps {
  onSpeakingStateChange: (isSpeaking: boolean) => void;
  onChatUpdate?: (messages: Message[]) => void;
  currentMood?: MoodEntry | null;
}

export default function ChatBox({ onSpeakingStateChange, onChatUpdate, currentMood }: ChatBoxProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'leo', text: "Hi! I'm Leo! How is your tummy feeling?", timestamp: new Date() }
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

<<<<<<< Updated upstream
  // Notify parent when messages change
  useEffect(() => {
    if (onChatUpdate) {
      onChatUpdate(messages);
    }
  }, [messages, onChatUpdate]);

  // React to mood changes - Leo acknowledges the mood
  useEffect(() => {
    if (currentMood) {
      const moodResponses: Record<string, string> = {
        '😊': "I'm so happy you're feeling good today! 🌟",
        '😐': "It's okay to feel just okay. I'm here if you want to talk!",
        '😢': "I'm sorry you're feeling sad. Would a hug help? 🤗",
        '😫': "Being tired is tough! Make sure to rest and drink water! 💧",
        '🤒': "Oh no, you're not feeling well! Should we tell a grown-up? 🏥",
      };
      
      const response = moodResponses[currentMood.mood] || "Thanks for telling me how you feel!";
      setMessages(prev => [...prev, { 
        role: 'leo', 
        text: response,
        timestamp: new Date()
      }]);
    }
  }, [currentMood]);
=======
  // Convert markdown-style **text** to bold and *text* to italic
  const renderMessage = (text: string) => {
    // First handle bold (**text**), then italic (*text*)
    const parts = text.split(/(\*\*.*?\*\*|\*[^*].*?\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        // Bold text
        const boldText = part.slice(2, -2);
        return <strong key={i}>{boldText}</strong>;
      } else if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
        // Italic text (but not bold)
        const italicText = part.slice(1, -1);
        return <em key={i}>{italicText}</em>;
      }
      return <span key={i}>{part}</span>;
    });
  };
>>>>>>> Stashed changes

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = input;
    const timestamp = new Date();
    setMessages(prev => [...prev, { role: 'user', text: userMsg, timestamp }]);
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
          condition: "diabetes",
          current_mood: currentMood?.label || null
        })
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let leoReply = "";

      setMessages(prev => [...prev, { role: 'leo', text: "...", timestamp: new Date() }]);

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
            {renderMessage(m.text)}
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