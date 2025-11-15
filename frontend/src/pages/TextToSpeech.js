// src/pages/TextToSpeech.js
import React, { useState, useRef, useEffect } from "react";
import { ArrowLeft, Upload, Volume2, Image as ImageIcon, FileText } from "lucide-react";
import { Link } from "react-router-dom";
import * as pdfjsLib from "pdfjs-dist";
import Tesseract from "tesseract.js";
import { Document, Packer, Paragraph } from "docx";

// PDF worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/3.3.122/pdf.worker.min.js`;

export default function TextToSpeech() {
  const [text, setText] = useState("Enter or upload text...");
  const [rate, setRate] = useState(1.0);
  const [pitch, setPitch] = useState(1.0);
  const [volume, setVolume] = useState(1.0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);

  const fileRef = useRef(null);
  const utterRef = useRef(null);

  // Load available voices
  useEffect(() => {
    function loadVoices() {
      const v = window.speechSynthesis.getVoices();
      setVoices(v);
      if (v.length > 0) setSelectedVoice(v[0].name);
    }
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);

  // ========== FILE HANDLERS ==========
  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const ext = file.name.toLowerCase();

    if (ext.endsWith(".txt")) {
      const txt = await file.text();
      setText(txt);

    } else if (ext.endsWith(".pdf")) {
      extractPDF(file);

    } else if (ext.endsWith(".docx")) {
      extractDOCX(file);

    } else if (ext.endsWith(".jpg") || ext.endsWith(".png") || ext.endsWith(".jpeg")) {
      extractImage(file);

    } else {
      alert("Unsupported file type");
    }

    e.target.value = "";
  }

  // ----- Extract text from PDF -----
  async function extractPDF(file) {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let finalText = "";

    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      finalText += content.items.map((t) => t.str).join(" ") + "\n\n";
    }

    setText(finalText);
  }

  // ----- Extract DOCX -----
  async function extractDOCX(file) {
    const buffer = await file.arrayBuffer();
    const doc = await Document.load(buffer);
    let finalText = "";

    doc.paragraphs.forEach((p) => {
      p.children.forEach((child) => {
        if (child.text) finalText += child.text + " ";
      });
      finalText += "\n\n";
    });

    setText(finalText);
  }

  // ----- Extract text from image (OCR) -----
  async function extractImage(file) {
    const { data } = await Tesseract.recognize(file, "eng", {
      logger: (m) => console.log(m),
    });
    setText(data.text);
  }

  // ========== SPEECH FUNCTIONS ==========
  function play() {
    if (!text.trim()) return;
    window.speechSynthesis.cancel();

    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = rate;
    utter.pitch = pitch;
    utter.volume = volume;

    // Set voice
    const voiceObj = voices.find((v) => v.name === selectedVoice);
    if (voiceObj) utter.voice = voiceObj;

    utter.onend = () => setIsPlaying(false);

    utterRef.current = utter;
    setIsPlaying(true);
    window.speechSynthesis.speak(utter);
  }

  function stop() {
    window.speechSynthesis.cancel();
    setIsPlaying(false);
  }

  return (
    <div className="app-bg min-h-screen flex items-center justify-center p-6">
      <div className="glass-card center-max p-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <Link to="/" className="inline-flex items-center gap-2 text-sm text-gray-600">
            <ArrowLeft size={16} /> Back
          </Link>
          <h2 className="font-bold text-lg">Text to Speech</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Text Area */}
          <div className="col-span-2">
            <label className="font-semibold">Text</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={12}
              className="w-full p-4 mt-2 rounded-lg"
            />

            <div className="flex gap-2 mt-4">
              <button onClick={play} disabled={isPlaying} className="px-4 py-2 rounded bg-green-600 text-white">
                Play
              </button>
              <button onClick={stop} disabled={!isPlaying} className="px-4 py-2 rounded border">
                Stop
              </button>
            </div>
          </div>

          {/* Controls */}
          <div className="col-span-1 space-y-4">

            {/* Upload Box */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="font-semibold flex items-center gap-2 mb-2">
                <Upload size={18} /> Upload File
              </label>
              <input
                type="file"
                accept=".txt,.pdf,.docx,.png,.jpg,.jpeg"
                onChange={handleFileUpload}
                className="text-sm"
              />
            </div>

            {/* Speed */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="block font-semibold mb-1">Speed: {rate}x</label>
              <input type="range" min="0.5" max="2" step="0.1" value={rate}
                     onChange={(e) => setRate(Number(e.target.value))} />
            </div>

            {/* Pitch */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="block font-semibold mb-1">Pitch: {pitch}</label>
              <input type="range" min="0" max="2" step="0.1" value={pitch}
                     onChange={(e) => setPitch(Number(e.target.value))} />
            </div>

            {/* Volume */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="block font-semibold mb-1">Volume: {Math.round(volume * 100)}%</label>
              <input type="range" min="0" max="1" step="0.05" value={volume}
                     onChange={(e) => setVolume(Number(e.target.value))} />
            </div>

            {/* Voice selection */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="block font-semibold mb-2">Voice</label>
              <select
                value={selectedVoice || ""}
                onChange={(e) => setSelectedVoice(e.target.value)}
                className="w-full p-2 rounded border"
              >
                {voices.map((v, index) => (
                  <option key={index} value={v.name}>{v.name}</option>
                ))}
              </select>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
