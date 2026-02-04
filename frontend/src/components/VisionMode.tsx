import React, { useRef, useState, useEffect, useCallback } from 'react';
import Webcam from 'react-webcam';
import * as tf from '@tensorflow/tfjs';
import * as cocoSsd from '@tensorflow-models/coco-ssd';
import '../App.css';

interface VisionModeProps {
  onClose: () => void;
  onObjectDetected?: (prediction: cocoSsd.DetectedObject[]) => void;
}

const VisionMode: React.FC<VisionModeProps> = ({ onClose, onObjectDetected }) => {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [model, setModel] = useState<cocoSsd.ObjectDetection | null>(null);
  const [loading, setLoading] = useState(true);
  const [predictions, setPredictions] = useState<cocoSsd.DetectedObject[]>([]);

  // Load the model
  useEffect(() => {
    const loadModel = async () => {
      try {
        console.log("Loading TensorFlow model...");
        await tf.ready();
        const loadedModel = await cocoSsd.load({
          base: 'mobilenet_v2' // Switched to standard model for better accuracy
        });
        setModel(loadedModel);
        setLoading(false);
        console.log("Model loaded successfully");
      } catch (err) {
        console.error("Failed to load model", err);
        setLoading(false);
      }
    };
    loadModel();
  }, []);

  // Run detection
  const detect = useCallback(async () => {
    if (
      model &&
      webcamRef.current &&
      webcamRef.current.video &&
      webcamRef.current.video.readyState === 4
    ) {
      const video = webcamRef.current.video;
      const videoWidth = video.videoWidth;
      const videoHeight = video.videoHeight;

      // Force video width/height to match intrinsic
      // This prevents the webcam from squishing the feed if CSS forces it
      video.width = videoWidth;
      video.height = videoHeight;

      // Set canvas dimensions to match the video
      if (canvasRef.current) {
        canvasRef.current.width = videoWidth;
        canvasRef.current.height = videoHeight;
      }

      // Detect objects with standard threshold
      const detected = await model.detect(video, undefined, 0.5);
      setPredictions(detected);

      if (onObjectDetected) {
        onObjectDetected(detected);
      }

      // Draw mesh
      const ctx = canvasRef.current?.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, videoWidth, videoHeight);

        detected.forEach((prediction) => {
          let [x, y, width, height] = prediction['bbox'];

          // Clip bounding box to video dimensions
          x = Math.max(0, x);
          y = Math.max(0, y);
          width = Math.min(videoWidth - x, width);
          height = Math.min(videoHeight - y, height);

          const text = prediction['class'];
          const score = (prediction['score'] * 100).toFixed(1);

          // Draw Bounding Box
          const color = '#00FF00'; // Matrix Green
          ctx.strokeStyle = color;
          ctx.lineWidth = 4;
          ctx.beginPath();
          ctx.rect(x, y, width, height);
          ctx.stroke();

          // Fill Box (semi-transparent)
          ctx.fillStyle = 'rgba(0, 255, 0, 0.1)';
          ctx.fill();

          // Draw Label Background
          ctx.fillStyle = color;
          const textWidth = ctx.measureText(text + " " + score + "%").width;
          const labelY = y - 25 < 0 ? y : y - 25;
          ctx.fillRect(x, labelY, textWidth + 10, 25);

          // Draw Label Text
          ctx.fillStyle = '#000000';
          ctx.font = 'bold 18px Arial';
          ctx.fillText(text + "  " + score + "%", x + 5, labelY + 18);
        });
      }
    }

  }, [model, onObjectDetected]);

  useEffect(() => {
    if (!loading && model) {
      // Use setTimeout loop to throttle detection to ~10fps
      let animationId: number;

      const loop = async () => {
        const start = Date.now();
        await detect();
        const end = Date.now();
        const processingTime = end - start;

        // Cap at ~10 FPS (100ms interval) max to save CPU
        const delay = Math.max(0, 100 - processingTime);
        animationId = window.setTimeout(loop, delay);
      };

      loop();

      return () => clearTimeout(animationId);
    }
  }, [loading, model, detect]);

  return (
    <div className="vision-overlay">
      <div className="vision-container">
        {loading && (
          <div className="vision-loading">
            <div className="vision-spinner">🦁</div>
            <p>Leo is waking up his eyes...</p>
          </div>
        )}

        <Webcam
          ref={webcamRef}
          muted={true}
          className="vision-webcam"
          screenshotFormat="image/jpeg"
          // Removed fixed width/height constraints so it uses camera native ratio
          videoConstraints={{
            facingMode: "environment"
          }}
          style={{ width: '100%', height: 'auto' }} // Ensure CSS respects ratio
          onUserMediaError={(err) => console.error("Webcam Error:", err)}
        />

        <canvas
          ref={canvasRef}
          className="vision-canvas"
          style={{ width: '100%', height: '100%', objectFit: 'contain' }} // Ensure canvas scales with video
        />

        <div className="vision-hud">
          {predictions.length > 0 ? (
            <div className="vision-status active">
              Found: {predictions.map(p => p.class).join(', ')}
            </div>
          ) : (
            <div className="vision-status">
              Scanning...
            </div>
          )}

          <button className="vision-close-btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default VisionMode;
