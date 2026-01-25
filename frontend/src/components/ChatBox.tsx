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
  onHelpDetected?: () => void;
  sosTrigger?: number;
  isKidMode?: boolean;
  childName?: string;
  childId?: string;
  childCondition?: string;
  childAge?: number;
}

export default function ChatBox({ onSpeakingStateChange, onChatUpdate, currentMood, onHelpDetected, sosTrigger, isKidMode = true, childName, childId, childCondition = 'diabetes', childAge = 7 }: ChatBoxProps) {
  const getInitialMessage = () => {
    if (isKidMode) {
      return `Hi${childName ? ` ${childName}` : ''}! I'm Leo! How is your tummy feeling? 🦁`;
    }
    return `Hello. I'm Leo, ${childName ? `${childName}'s` : 'your child\'s'} health companion. I can help answer questions about their health management. How may I assist you today?`;
  };
  
  const [messages, setMessages] = useState<Message[]>([
    { role: 'leo', text: getInitialMessage(), timestamp: new Date() }
  ]);
  
  // Reset messages when mode changes
  useEffect(() => {
    setMessages([
      { role: 'leo', text: getInitialMessage(), timestamp: new Date() }
    ]);
  }, [isKidMode, childName]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastTranscriptRef = useRef<string>('');
  
  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognitionAPI();
      recognitionRef.current.continuous = true;  // Keep listening
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onresult = (event: SpeechRecognitionEvent) => {
        let transcript = '';
        let isFinal = false;
        
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            isFinal = true;
          }
        }
        
        setInput(transcript);
        lastTranscriptRef.current = transcript;
        
        // Reset silence timeout on each result
        if (silenceTimeoutRef.current) {
          clearTimeout(silenceTimeoutRef.current);
        }
        
        // If we got a final result, wait 1.5 seconds of silence before stopping
        if (isFinal) {
          silenceTimeoutRef.current = setTimeout(() => {
            if (recognitionRef.current && lastTranscriptRef.current) {
              recognitionRef.current.stop();
            }
          }, 1500); // 1.5 second delay after speech ends
        }
      };
      
      recognitionRef.current.onend = () => {
        setIsRecording(false);
        if (silenceTimeoutRef.current) {
          clearTimeout(silenceTimeoutRef.current);
        }
      };
      
      recognitionRef.current.onerror = () => {
        setIsRecording(false);
        if (silenceTimeoutRef.current) {
          clearTimeout(silenceTimeoutRef.current);
        }
      };
    }
    
    return () => {
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
    };
  }, []);
  
  const toggleRecording = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition not supported in this browser. Try Chrome!');
      return;
    }
    
    if (isRecording) {
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      setInput('');
      lastTranscriptRef.current = '';
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Notify parent when typing state changes
  useEffect(() => {
    onSpeakingStateChange(isTyping);
  }, [isTyping, onSpeakingStateChange]);

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

  // React to SOS button being pressed
  useEffect(() => {
    if (sosTrigger && sosTrigger > 0) {
      setMessages(prev => [...prev, { 
        role: 'leo', 
        text: "Oh no! Are you okay? 😰 I'm here for you! A grown-up can help - use the numbers on the screen! 🆘💕",
        timestamp: new Date()
      }]);
    }
  }, [sosTrigger]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = input;
    const timestamp = new Date();
    
    // Check for help keyword
    if (userMsg.toLowerCase().includes('help')) {
      onHelpDetected?.();
    }
    
    setMessages(prev => [...prev, { role: 'user', text: userMsg, timestamp }]);
    setInput('');
    setIsTyping(true); // <--- Triggers Lion Mouth Open

    try {
      const response = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: childId || "demo_child",
          child_id: childId || "demo_child",
          child_name: childName || "friend",
          message: userMsg,
          age: childAge,
          condition: childCondition,
          current_mood: currentMood?.label || null,
          is_kid_mode: isKidMode
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
          disabled={isTyping || isRecording}
        />
        <button 
          className={`mic-button ${isRecording ? 'recording' : ''}`}
          onClick={toggleRecording}
          disabled={isTyping}
          title={isRecording ? 'Stop recording' : 'Push to talk'}
        >
          {isRecording ? '🔴' : '🎤'}
        </button>
        <button onClick={sendMessage} disabled={isTyping || !input.trim()}>
          {isTyping ? '🦁' : '➤'}
        </button>
      </div>
    </div>
  );
}