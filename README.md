<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/lion_1f981.png" width="120" alt="Leo the Lion"/>
</p>

<h1 align="center">Leo the Lion!</h1>
<h3 align="center">AI-Powered Health Companion for Children with Chronic Conditions</h3>

<p align="center">
  <strong>TELUS Hackathon 2026 Submission</strong><br/>
  Track 3: AI + Healthcare
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-18.x-61DAFB?style=for-the-badge&logo=react" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript" alt="TypeScript"/>
</p>

---

## 🌟 The Problem

**500,000+ children** in North America live with chronic conditions like diabetes and asthma. Current health apps are:
- 😰 **Scary** - Clinical interfaces designed for adults
- 📊 **Confusing** - Complex data that overwhelms children
- 😔 **Boring** - No engagement or motivation

**Parents struggle** to track medications, understand symptoms, and communicate health info to their kids.

---

## 💡 Our Solution

**Leo the Lion** is a friendly AI companion that transforms health management into an engaging, game-like experience.

### For Kids 🧒
- 🎮 **Gamified Interface** - XP, levels, streaks, and achievements
- 🗣️ **Natural Conversations** - Talk to Leo like a friend (voice or text!)
- 🌈 **Kid-Friendly Language** - "Leo needs Magic Fuel!" instead of "Low glucose alert"
- 💭 **Daily Motivation** - 50 unique thoughts of the day
- 🆘 **Safety First** - One-tap SOS with emergency contacts

### For Parents 👨‍👩‍👧
- 📊 **Real-time Dashboard** - Live health metrics at a glance
- 💊 **Medication Tracking** - Log insulin, inhalers, and more
- 🔒 **Password Protected** - Kids can't access parent mode
- 🧠 **Leo Remembers** - Set rules like "no chocolate" that Leo enforces
- 📝 **Chat Summaries** - See what your child talked about with Leo

---

## 🏗️ Technical Architecture

### 🎨 Frontend (React + TypeScript + CSS)
- Kid Mode (Game UI)
- Parent Dashboard
- Leo Chat (Streaming)
- Voice Input (Web Speech API)

⬇️ communicates with

### ⚡ Backend (FastAPI + Python)
- Health Simulator (Real-time)
- Chat Memory (Per-child)
- Child Profiles (JSON Storage)

⬇️ powered by

### 🧠 AI Brain Service
- DeepSeek (Health Analysis)
- Gemma 3 (Kid-Friendly Responses)
- Local RAG (Medical Safety)


---

## 🤖 AI/ML Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Primary LLM** | Google Gemma 3 27B | Kid-friendly response generation |
| **Analysis LLM** | DeepSeek | Health data analysis & recommendations |
| **Embeddings** | SentenceTransformers | Semantic search for medical accuracy |
| **RAG Engine** | Custom (scikit-learn) | Retrieval-Augmented Generation for safety |
| **Voice Input** | Web Speech API | Push-to-talk for young children |
| **Streaming** | Server-Sent Events | Real-time chat responses |

### LLM Integration Highlights
- **Dual-LLM Architecture**: DeepSeek analyzes health patterns, Gemma crafts child-friendly responses
- **Context-Aware Prompting**: Leo adapts tone based on kid mode vs parent mode
- **Memory System**: Per-child chat history + parent instructions persist across sessions
- **Fallback Intelligence**: 100+ contextual offline responses when API is unavailable

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎤 **Voice Input** | Push-to-talk with 1.5s silence detection |
| 👶 **Multi-Child Profiles** | Each child has unique history & settings |
| 🔐 **Parent Password** | Secure access with forgot password recovery |
| 📱 **Responsive Design** | Works on desktop, tablet, mobile |
| 🌴 **Jungle Theme** | Immersive, kid-friendly visual design |
| 💬 **Streaming Chat** | Real-time AI responses, word by word |
| 📊 **Live Metrics** | Heart rate, glucose, SpO2 simulation |
| 💊 **Medication Reminders** | Smart insulin/inhaler notifications |
| 🆘 **Emergency SOS** | One-tap access to emergency contacts |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### 1. Clone the Repository
```bash
git clone https://github.com/your-team/leo-the-lion.git
cd leo-the-lion
```

### 2. Set Up Environment Variables
```bash
# Create .env file in root directory
cp .env.example .env

# Add your API keys
TELUS_API_BASE="https://3ca9s.paas.ai.telus.com"
QWEN_API_KEY="your_qwen_key"
GEMMA_API_KEY="your_gemma_key"
DEEPSEEK_API_KEY="your_deepseek_key"
```

### 3. Start the Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI server
python -m uvicorn backend.main:app --reload

# Run the mock data
python -m backend.sensor_stream
```


### 4. Start the Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Open in Browser
Visit `http://localhost:5173` and start exploring!

---

## 🎮 Demo Walkthrough

1. **Select a Child** - Click the profile dropdown (Maya or Ethan)
2. **Chat with Leo** - Type or use the 🎤 microphone button
3. **Check Mood** - Click an emoji to tell Leo how you feel
4. **Switch to Parent Mode** - Click 🔒 and enter password: `1234`
5. **View Dashboard** - See live metrics, log medications
6. **Set Rules** - Tell Leo "if Maya asks for candy, say no"
7. **Add a Child** - In parent mode, click + to create a profile

---

## 📁 Project Structure

```
Team/
├── backend/
│   ├── main.py              # FastAPI endpoints
│   ├── models.py            # Pydantic schemas
│   ├── brain.py             # Health analysis logic
│   ├── chat_memory.py       # Per-child chat storage
│   ├── child_profiles.py    # Profile management
│   ├── data_simulator.py    # Health data simulation
│   ├── scenarios.py         # Health episode scenarios
│   ├── rag_engine.py        # RAG for medical safety
│   └── services/
│       └── brain_service.py # LLM integration
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main application
│   │   ├── App.css          # Global styles
│   │   └── components/
│   │       ├── ChatBox.tsx      # Chat interface + voice
│   │       ├── LeoAvatar.tsx    # Animated lion
│   │       ├── MoodTracker.tsx  # Emoji mood selector
│   │       ├── ChildSelector.tsx # Profile switcher
│   │       └── ParentDashboard.tsx # Parent view
│   └── package.json
│
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

---

## 🛡️ Safety & Privacy

- **No Real Medical Advice**: Leo is a companion, not a doctor
- **Local Data Storage**: All data stored locally in JSON files
- **Parent Controls**: Password-protected adult features
- **Emergency Ready**: Quick access to real emergency numbers
- **Kid-Safe Language**: Carefully crafted prompts prevent inappropriate content

---

## 🏆 Hackathon Highlights

### Innovation
- First AI companion designed specifically for children's chronic disease management
- Dual-mode interface (Kid/Parent) with seamless switching
- Voice-first design for children who can't type

### Technical Excellence
- Real-time streaming AI responses
- Multi-model architecture for safety and engagement
- Per-child memory and parent instruction following

## 🌍 Impact & Use Cases

### Real-World Impact
- Reduces anxiety for children managing chronic conditions
- Improves medication adherence through gamification
- Gives parents peace of mind with real-time insights

### Use Cases
- Daily diabetes management for children
- Asthma monitoring and trigger awareness
- Emotional support during school, play, and sleep
- Multi-child health tracking for families
- Safe, guided health conversations without medical jargon


---

## 👥 Team

Built with ❤️ for TELUS Hackathon 2026
| Name                 |GitHub         |
|----------------------|---------------|
| Omar Abbasi          | Gfewq         |
| Ujjawal Singh        | ujjawalsuii   |
| Ishan Raj            | isr808        |
| Natasha Krishnakanth | natashakk0602 |
---

## 📄 License

MIT License - Feel free to build upon Leo!

---

<p align="center">
  <strong>🦁 Leo the Lion - Because every cub deserves a friend.</strong>
</p>
