// FINAL CLEAN VERSION – ALL OLD FEATURES + ALL NEW FEATURES

import React, { useState, useEffect, useRef } from "react";
import { ArrowLeft } from "lucide-react";
import { SketchPicker } from "react-color";
import { Link } from "react-router-dom";

// THIRD-PARTY LIBRARIES YOU MUST INSTALL
// npm install pdfjs-dist mammoth tesseract.js

import * as pdfjsLib from "pdfjs-dist";
import mammoth from "mammoth";
import Tesseract from "tesseract.js";

pdfjsLib.GlobalWorkerOptions.workerSrc =
  `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.js`;

export default function DyslexiaFont() {
  const [text, setText] = useState("Type or paste text here...");
  const [font, setFont] = useState("normal");
  const [fontSize, setFontSize] = useState(20);
  const [lineHeight, setLineHeight] = useState(1.6);
  const [letterSpacing, setLetterSpacing] = useState(0);
  const [bgColor, setBgColor] = useState("#fffef0");
  const [textColor, setTextColor] = useState("#222222");

  const [showBgPicker, setShowBgPicker] = useState(false);
  const [showTextPicker, setShowTextPicker] = useState(false);

  const fileInputRef = useRef(null);

  // TTS
  const [rate, setRate] = useState(1.0);
  const [isReading, setIsReading] = useState(false);

  function playTTS() {
    if (!("speechSynthesis" in window)) {
      alert("Browser does not support TTS");
      return;
    }
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = rate;
    utter.onend = () => setIsReading(false);

    setIsReading(true);
    window.speechSynthesis.speak(utter);
  }

  function stopTTS() {
    window.speechSynthesis.cancel();
    setIsReading(false);
  }

  // Save user preferences
  useEffect(() => {
    localStorage.setItem(
      "dyslexia_ui_settings",
      JSON.stringify({
        font,
        fontSize,
        lineHeight,
        letterSpacing,
        bgColor,
        textColor,
      })
    );
  }, [font, fontSize, lineHeight, letterSpacing, bgColor, textColor]);

  // Load preferences
  useEffect(() => {
    try {
      const s = JSON.parse(localStorage.getItem("dyslexia_ui_settings") || "{}");
      if (s.font) setFont(s.font);
      if (s.fontSize) setFontSize(s.fontSize);
      if (s.lineHeight) setLineHeight(s.lineHeight);
      if (s.letterSpacing) setLetterSpacing(s.letterSpacing);
      if (s.bgColor) setBgColor(s.bgColor);
      if (s.textColor) setTextColor(s.textColor);
    } catch {}
  }, []);

  // FILE UPLOAD HANDLING (TXT + PDF + DOCX + IMAGES)
  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.toLowerCase();

    if (ext.endsWith(".txt")) {
      const txt = await file.text();
      setText(txt);
    } 
    else if (ext.endsWith(".pdf")) {
      readPDF(file);
    } 
    else if (ext.endsWith(".docx")) {
      readDOCX(file);
    }
    else if ([".png", ".jpg", ".jpeg", ".bmp"].some(x => ext.endsWith(x))) {
      readImage(file);
    }
    else {
      alert("Unsupported file type");
    }

    e.target.value = "";
  }

  // PDF extraction
  async function readPDF(file) {
    const buffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: buffer }).promise;
    let fullText = "";

    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      fullText += content.items.map((item) => item.str).join(" ") + "\n";
    }

    setText(fullText);
  }

  // DOCX extraction
  async function readDOCX(file) {
    const arrayBuffer = await file.arrayBuffer();
    const result = await mammoth.extractRawText({ arrayBuffer });
    setText(result.value);
  }

  // IMAGE OCR extraction
  async function readImage(file) {
    const { data: { text } } = await Tesseract.recognize(file, "eng");
    setText(text);
  }

  const editorStyle = {
    fontSize: `${fontSize}px`,
    lineHeight: lineHeight,
    letterSpacing: `${letterSpacing}px`,
    color: textColor,
    backgroundColor: bgColor,
  };

  return (
    <div className="app-bg min-h-screen flex items-center justify-center p-6">
      <div className="glass-card center-max p-6">

        {/* HEADER */}
        <div className="flex items-center justify-between mb-4">
          <Link to="/" className="inline-flex items-center gap-2 text-sm text-gray-600">
            <ArrowLeft size={16} /> Back
          </Link>
          <h2 className="font-bold text-lg">Dyslexia Font</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

          {/* LEFT PANEL – ALL SETTINGS */}
          <div className="space-y-4 col-span-1">

            {/* Font */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="font-semibold">Font</label>
              <select
                value={font}
                onChange={(e) => setFont(e.target.value)}
                className="w-full p-2 mt-2 rounded border"
              >
                <option value="normal">Normal</option>
                <option value="opendys">OpenDyslexic (if loaded)</option>
              </select>
            </div>

            {/* Spacing */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="block font-semibold">Font size: {fontSize}px</label>
              <input
                type="range"
                min="14" max="48"
                value={fontSize}
                onChange={(e) => setFontSize(Number(e.target.value))}
                className="w-full"
              />

              <label className="block font-semibold mt-3">
                Line spacing: {lineHeight}
              </label>
              <input
                type="range"
                min="1" max="2.4" step="0.1"
                value={lineHeight}
                onChange={(e) => setLineHeight(Number(e.target.value))}
                className="w-full"
              />

              <label className="block font-semibold mt-3">
                Letter spacing: {letterSpacing}px
              </label>
              <input
                type="range"
                min="0" max="4" step="0.1"
                value={letterSpacing}
                onChange={(e) => setLetterSpacing(Number(e.target.value))}
                className="w-full"
              />
            </div>

            {/* Background color */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="font-semibold">Background Color</label>
              <div className="flex gap-2 mt-2">
                <button className="w-8 h-8 rounded" style={{ background: "#fffef0" }} onClick={() => setBgColor("#fffef0")} />
                <button className="w-8 h-8 rounded" style={{ background: "#f7fbff" }} onClick={() => setBgColor("#f7fbff")} />
                <button className="w-8 h-8 rounded" style={{ background: "#f3fff4" }} onClick={() => setBgColor("#f3fff4")} />
                <button className="px-2 py-1 border rounded" onClick={() => setShowBgPicker(!showBgPicker)}>Custom</button>
              </div>
              {showBgPicker && <SketchPicker color={bgColor} onChangeComplete={(c) => setBgColor(c.hex)} className="mt-2" />}
            </div>

            {/* Text color */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="font-semibold">Text Color</label>
              <div className="flex gap-2 mt-2">
                <button className="w-8 h-8 rounded" style={{ background: "#222" }} onClick={() => setTextColor("#222")} />
                <button className="w-8 h-8 rounded" style={{ background: "#3b3b6b" }} onClick={() => setTextColor("#3b3b6b")} />
                <button className="px-2 py-1 border rounded" onClick={() => setShowTextPicker(!showTextPicker)}>Custom</button>
              </div>
              {showTextPicker && <SketchPicker color={textColor} onChangeComplete={(c) => setTextColor(c.hex)} className="mt-2" />}
            </div>

            {/* FILE UPLOAD */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="font-semibold">Upload File</label>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.pdf,.docx,.png,.jpg,.jpeg,.bmp"
                onChange={handleFileUpload}
                className="mt-2"
              />
            </div>

            {/* TTS */}
            <div className="p-3 bg-white/60 rounded-lg">
              <label className="font-semibold">Reading Speed: {rate}x</label>
              <input
                type="range"
                min="0.5" max="2" step="0.1"
                value={rate}
                onChange={(e) => setRate(Number(e.target.value))}
                className="w-full"
              />

              <div className="flex gap-2 mt-3">
                <button onClick={playTTS} className="px-4 py-2 rounded bg-green-600 text-white">Play</button>
                <button onClick={stopTTS} className="px-4 py-2 rounded border">Stop</button>
              </div>
            </div>

          </div>

          {/* RIGHT SIDE – TEXT EDITOR */}
          <div className="col-span-3">
            <label className="font-semibold">Editor</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={12}
              style={editorStyle}
              className={`w-full p-4 mt-2 rounded-lg resize-vertical ${font === "opendys" ? "font-opendys" : ""}`}
            />

            <div className="flex gap-2 mt-3">
              <button
                onClick={() => navigator.clipboard.writeText(text)}
                className="px-4 py-2 rounded bg-indigo-600 text-white"
              >
                Copy
              </button>

              <button
                onClick={() => setText("")}
                className="px-4 py-2 rounded border"
              >
                Clear
              </button>

              <button
                onClick={() => {
                  const blob = new Blob([text], { type: "text/plain" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = "text.txt";
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                className="px-4 py-2 rounded border"
              >
                Download .txt
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
