import { useState, useEffect } from 'react';
import ChatBox from './components/ChatBox';
import LeoAvatar from './components/LeoAvatar'; 
import './App.css';

// 📊 Define the shape of our data (Matches Python Backend)
interface UserStats {
  xp: number;
  level: number;
  status: string;
}

function App() {
  // 1. STATE: Health Stats & Speaking Logic
  const [stats, setStats] = useState<UserStats>({ xp: 0, level: 1, status: 'Connecting...' });
  const [isLeoTalking, setIsLeoTalking] = useState(false); 

  // 2. POLLING: Check the backend every 2 seconds for Health/XP updates
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:8000/'); 
        const data = await res.json();
        setStats(data.stats);
      } catch (e) {
        console.log("Backend offline (Leo is sleeping)");
      }
    };
    
    fetchStats(); // Run once immediately
    const interval = setInterval(fetchStats, 2000); // Run every 2s
    return () => clearInterval(interval);
  }, []);

  // 3. LOGIC: Determine Status Color
  // If status contains "Help" or "Check", turn red/yellow
  const isDanger = stats.status.includes('Help') || stats.status.includes('Check');
  const statusClass = isDanger ? 'status-warn' : 'status-good';

  return (
    <div className="app-wrapper">
      {/* --- HUD BAR (Top) --- */}
      <div className="status-hud">
        <div className="stat-pill">⭐ Level {stats.level}</div>
        <div className="stat-pill">✨ {stats.xp} XP</div>
        <div className={`stat-pill ${statusClass}`}>
          {/* Ensure status is never empty */}
          ❤️ {stats.status || "Loading..."}
        </div>
      </div>

      {/* --- MAIN GAME SCENE --- */}
      <main className="game-scene">
        
        {/* LEFT: The Avatar */}
        <div className="avatar-zone">
          {/* 🦁 Pass the speaking state so his mouth moves! */}
          <LeoAvatar isSpeaking={isLeoTalking} />
        </div>
        
        {/* RIGHT: The Chat */}
        <div className="chat-zone">
          {/* 🗣️ ChatBox tells App when it starts/stops typing */}
          <ChatBox onSpeakingStateChange={setIsLeoTalking} />
        </div>

      </main>
    </div>
  );
}

export default App;