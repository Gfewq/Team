import { useState, useEffect, useRef } from 'react'
import LeoAvatar from './components/LeoAvatar'
import Tree from './components/Tree'
import './App.css'

function App() {
  const [dialogue, setDialogue] = useState("Hi there! I'm Leo the Lion. How can I help you today?")
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [speechEnabled, setSpeechEnabled] = useState(true)
  const speechRef = useRef<SpeechSynthesisUtterance | null>(null)

  // Speak the dialogue when it changes (if speech is enabled)
  useEffect(() => {
    if (speechEnabled && 'speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel()
      
      // Create new utterance - friendly lion voice
      const utterance = new SpeechSynthesisUtterance(dialogue)
      utterance.rate = 0.9   // Natural pace
      utterance.pitch = 1.15 // Slightly warm, not too high
      utterance.volume = 1.0
      
      // Find a warm male voice for friendly lion character
      const voices = window.speechSynthesis.getVoices()
      const lionVoice = voices.find(voice => 
        voice.name.includes('Daniel') ||    // Mac - UK male, warm
        voice.name.includes('Alex') ||      // Mac - US male
        voice.name.includes('Fred') ||      // Mac - friendly male
        voice.name.includes('David') ||     // Windows - male
        voice.name.includes('Mark') ||      // Windows - male
        voice.name.includes('George')       // UK male
      ) || voices.find(voice =>
        voice.lang.startsWith('en') && 
        (voice.name.toLowerCase().includes('male') || voice.name.includes('Google'))
      ) || voices[0]
      
      if (lionVoice) {
        utterance.voice = lionVoice
      }
      
      // Start speaking animation
      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      utterance.onerror = () => setIsSpeaking(false)
      
      speechRef.current = utterance
      window.speechSynthesis.speak(utterance)
    } else {
      setIsSpeaking(false)
    }
    
    return () => {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
    }
  }, [dialogue, speechEnabled])

  // Load voices (needed for some browsers)
  useEffect(() => {
    const loadVoices = () => {
      window.speechSynthesis.getVoices()
    }
    loadVoices()
    window.speechSynthesis.onvoiceschanged = loadVoices
  }, [])

  const toggleSpeech = () => {
    if (speechEnabled) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
    }
    setSpeechEnabled(!speechEnabled)
  }

  return (
    <div className="game-screen">
      {/* Background trees */}
      <Tree className="tree-far-left" />
      <Tree className="tree-left" />
      <Tree className="tree-right" flip={true} />
      <Tree className="tree-far-right" flip={true} />
      
      <div className="content-wrapper">
        <div className="avatar-section">
          <LeoAvatar isSpeaking={isSpeaking} />
        </div>
        <div className="dialogue-section">
          <div className="dialogue-box">
            <p>{dialogue}</p>
          </div>
          <button 
            className={`speech-toggle ${speechEnabled ? 'enabled' : 'disabled'}`}
            onClick={toggleSpeech}
            title={speechEnabled ? 'Turn speech off' : 'Turn speech on'}
          >
            {speechEnabled ? '🔊' : '🔇'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
