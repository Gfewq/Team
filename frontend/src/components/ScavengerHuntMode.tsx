import React, { useRef, useState, useEffect, useCallback } from 'react';
import Webcam from 'react-webcam';
import * as tf from '@tensorflow/tfjs';
import * as cocoSsd from '@tensorflow-models/coco-ssd';
import { useVoice } from '../hooks/useVoice';
import '../App.css';

interface ScavengerHuntModeProps {
    onClose: () => void;
    onAddXP: (amount: number) => void;
}

const TARGETS = [
    { id: 'cup', label: 'Cup', icon: '🥤' },
    { id: 'bottle', label: 'Bottle', icon: '🍾' },
    { id: 'book', label: 'Book', icon: '📚' },
    { id: 'cell phone', label: 'Phone', icon: '📱' },
    { id: 'person', label: 'Person', icon: '👤' },
    { id: 'banana', label: 'Banana', icon: '🍌' },
    { id: 'apple', label: 'Apple', icon: '🍎' },
    { id: 'keyboard', label: 'Keyboard', icon: '⌨️' },
    { id: 'mouse', label: 'Mouse', icon: '🖱️' },
    { id: 'laptop', label: 'Laptop', icon: '💻' }
];

const ScavengerHuntMode: React.FC<ScavengerHuntModeProps> = ({ onClose, onAddXP }) => {
    const webcamRef = useRef<Webcam>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [model, setModel] = useState<cocoSsd.ObjectDetection | null>(null);
    const [loading, setLoading] = useState(true);

    // Game State
    const [gameState, setGameState] = useState<'intro' | 'hunting' | 'found' | 'play_again'>('intro');
    const [target, setTarget] = useState<typeof TARGETS[0] | null>(null);
    const [countdown, setCountdown] = useState(3);

    // Voice
    const { speak } = useVoice();

    // Load the model
    useEffect(() => {
        const loadModel = async () => {
            try {
                console.log("Loading TensorFlow model...");
                await tf.ready();
                const loadedModel = await cocoSsd.load({
                    base: 'mobilenet_v2'
                });
                setModel(loadedModel);
                setLoading(false);
            } catch (err) {
                console.error("Failed to load model", err);
                setLoading(false);
            }
        };
        loadModel();
    }, []);

    // START GAME LOGIC
    useEffect(() => {
        if (!loading && model && gameState === 'intro') {
            // Pick a random target
            const randomTarget = TARGETS[Math.floor(Math.random() * TARGETS.length)];
            setTarget(randomTarget);

            // Start Countdown
            let count = 3;
            setCountdown(count);

            const timer = setInterval(() => {
                count--;
                if (count > 0) {
                    setCountdown(count);
                } else {
                    clearInterval(timer);
                    setGameState('hunting');
                    speak(`Find me a ${randomTarget.label}!`);
                }
            }, 1000);

            return () => clearInterval(timer);
        }
    }, [loading, model, gameState, speak]);

    // DETECTION LOOP
    const detect = useCallback(async () => {
        if (
            model &&
            webcamRef.current &&
            webcamRef.current.video &&
            webcamRef.current.video.readyState === 4 &&
            gameState === 'hunting' &&
            target
        ) {
            const video = webcamRef.current.video;
            const videoWidth = video.videoWidth;
            const videoHeight = video.videoHeight;

            // Force video width/height
            video.width = videoWidth;
            video.height = videoHeight;
            if (canvasRef.current) {
                canvasRef.current.width = videoWidth;
                canvasRef.current.height = videoHeight;
            }

            // Detect
            const detected = await model.detect(video, undefined, 0.5);

            // Check for target
            const foundTarget = detected.find(obj =>
                obj.class.toLowerCase() === target.id.toLowerCase() ||
                (target.id === 'cup' && obj.class === 'cup') // loose matching if needed
            );

            // Draw standard boxes
            const ctx = canvasRef.current?.getContext('2d');
            if (ctx) {
                ctx.clearRect(0, 0, videoWidth, videoHeight);
                detected.forEach(prediction => {
                    // Highlight TARGET in GOLD, others in white
                    const isTarget = prediction.class.toLowerCase() === target.id.toLowerCase();
                    const color = isTarget ? '#FFD700' : 'rgba(255, 255, 255, 0.5)';

                    const [x, y, width, height] = prediction.bbox;
                    ctx.strokeStyle = color;
                    ctx.lineWidth = isTarget ? 6 : 2;
                    ctx.strokeRect(x, y, width, height);

                    ctx.font = '18px Arial';
                    ctx.fillStyle = color;
                    ctx.fillText(prediction.class, x, y > 10 ? y - 5 : 10);
                });
            }

            if (foundTarget) {
                // FOUND IT!
                setGameState('found');
                speak(`You found a ${target.label}! Amazing work!`);
                onAddXP(50);

                // Wait 2 seconds then ask to play again
                setTimeout(() => {
                    setGameState('play_again');
                    speak("Do you want to play another round?");
                }, 3000);
            }
        }
    }, [model, gameState, target, speak, onAddXP]);

    useEffect(() => {
        if (gameState === 'hunting') {
            const interval = setInterval(() => {
                detect();
            }, 200); // 5 FPS check
            return () => clearInterval(interval);
        }
    }, [gameState, detect]);

    const handlePlayAgain = (play: boolean) => {
        if (play) {
            setGameState('intro');
        } else {
            onClose();
        }
    };

    return (
        <div className="vision-overlay scavenger-mode">
            <div className="vision-container">

                {/* WEBCAM LAYER */}
                <Webcam
                    ref={webcamRef}
                    muted={true}
                    className="vision-webcam"
                    screenshotFormat="image/jpeg"
                    videoConstraints={{ facingMode: "environment" }}
                    style={{ width: '100%', height: 'auto' }}
                />
                <canvas
                    ref={canvasRef}
                    className="vision-canvas"
                    style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />

                {/* UI OVERLAYS */}

                {/* 1. LOADING */}
                {loading && (
                    <div className="game-overlay loading">
                        <h1>🦁 preparing hunt...</h1>
                    </div>
                )}

                {/* 2. INTRO / COUNTDOWN */}
                {!loading && gameState === 'intro' && target && (
                    <div className="game-overlay intro">
                        <h2>Next Target:</h2>
                        <div className="target-card">
                            <span className="target-icon">{target.icon}</span>
                            <span className="target-name">{target.label}</span>
                        </div>
                        <div className="countdown">{countdown}</div>
                    </div>
                )}

                {/* 3. HUNTING HUD */}
                {!loading && gameState === 'hunting' && target && (
                    <div className="game-hud">
                        <div className="mission-box">
                            <span>Find: </span>
                            <span className="icon">{target.icon}</span>
                            <strong>{target.label}</strong>
                        </div>
                        <button className="quit-btn" onClick={onClose}>Quit ❌</button>
                    </div>
                )}

                {/* 4. SUCCESS */}
                {gameState === 'found' && target && (
                    <div className="game-overlay success">
                        <h1>🎉 FOUND IT! 🎉</h1>
                        <div className="target-card big">
                            <span className="target-icon">{target.icon}</span>
                        </div>
                        <h2>+50 XP</h2>
                    </div>
                )}

                {/* 5. PLAY AGAIN? */}
                {gameState === 'play_again' && (
                    <div className="game-overlay play-again">
                        <h2>Play Another Round? 🦁</h2>
                        <div className="choice-buttons">
                            <button className="choice-btn yes" onClick={() => handlePlayAgain(true)}>
                                YES ✅
                            </button>
                            <button className="choice-btn no" onClick={() => handlePlayAgain(false)}>
                                NO ❌
                            </button>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
};

export default ScavengerHuntMode;
