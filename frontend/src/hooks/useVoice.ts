import { useState, useEffect, useCallback } from 'react';

export const useVoice = () => {
    const [isMuted, setIsMuted] = useState(false);
    const [speaking, setSpeaking] = useState(false);
    const [supported, setSupported] = useState(false);
    const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);

    useEffect(() => {
        if ('speechSynthesis' in window) {
            setSupported(true);

            const loadVoices = () => {
                const availableVoices = window.speechSynthesis.getVoices();
                console.log("🦁 Logic: Loaded voices:", availableVoices.length);
                setVoices(availableVoices);
            };

            loadVoices();

            // Chrome loads voices asynchronously
            if (window.speechSynthesis.onvoiceschanged !== undefined) {
                window.speechSynthesis.onvoiceschanged = loadVoices;
            }
        } else {
            console.log("🦁 Logic: Text-to-Speech not supported");
        }
    }, []);

    const speak = useCallback((text: string) => {
        if (!supported || isMuted || !text) {
            console.log("🦁 Logic: Speak blocked", { supported, isMuted, text });
            return;
        }

        console.log("🦁 Logic: Leo is speaking:", text);

        // Cancel any current speech
        window.speechSynthesis.cancel();

        // Remove emojis so he doesn't read them (e.g. "Lion Face")
        const cleanText = text.replace(/([\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD10-\uDDFF])/g, '');

        const utterance = new SpeechSynthesisUtterance(cleanText);

        // Better voice selection logic - Priority: English Male
        const leosVoice =
            voices.find(v => v.name.includes('Google UK English Male')) ||
            voices.find(v => v.lang.startsWith('en') && v.name.includes('Male')) ||
            voices.find(v => v.name.includes('Daniel')) || // Good Safari/Mac Male voice
            voices.find(v => v.lang.startsWith('en') && !v.name.includes('Female')) ||
            voices.find(v => v.lang.startsWith('en')) ||
            voices[0];

        if (leosVoice) {
            console.log("🦁 Logic: Selected voice:", leosVoice.name);
            utterance.voice = leosVoice;
        } else {
            console.log("🦁 Logic: No specific voice found, using default");
        }

        utterance.pitch = 0.8; // Lower pitch for a big Lion voice! 🦁
        utterance.rate = 0.9;  // Slightly slower, more commanding
        utterance.volume = 1.0;

        utterance.onstart = () => setSpeaking(true);
        utterance.onend = () => setSpeaking(false);
        utterance.onerror = (e) => {
            console.error("🦁 Logic: Speech error", e);
            setSpeaking(false);
        };

        window.speechSynthesis.speak(utterance);
    }, [supported, isMuted, voices]);

    const toggleMute = useCallback(() => {
        setIsMuted(prev => {
            const newState = !prev;
            if (newState) {
                window.speechSynthesis.cancel();
                setSpeaking(false);
            }
            return newState;
        });
    }, []);

    return {
        speak,
        toggleMute,
        isMuted,
        speaking,
        supported
    };
};
