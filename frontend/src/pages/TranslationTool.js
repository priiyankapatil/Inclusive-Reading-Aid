// src/pages/TranslationTool.js
import React, { useState } from "react";
import { ArrowLeft, Upload } from "lucide-react";
import { Link } from "react-router-dom";

// Supported languages
const LANGS = [
  { code: "en", name: "English" },
  { code: "es", name: "Spanish" },
  { code: "fr", name: "French" },
  { code: "hi", name: "Hindi" },
  { code: "de", name: "German" },
  { code: "ta", name: "Tamil" },
  { code: "te", name: "Telugu" },
  { code: "ml", name: "Malayalam" },
  { code: "kn", name: "Kannada" }, // ✅ Added Kannada
];

// Helper: Read file text
function readFileContent(file) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.readAsText(file);
  });
}

export default function TranslationTool() {
  const [source, setSource] = useState("en");
  const [target, setTarget] = useState("es");
  const [input, setInput] = useState("Enter text to translate...");
  const [output, setOutput] = useState("");
  const [fileName, setFileName] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // Placeholder translation
  async function translate() {
    setOutput(`(Translation placeholder for ${target})\n\n${input}`);
  }

  // Handle text, pdf, docx
  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(file.name);

    if (file.type === "text/plain") {
      const text = await readFileContent(file);
      setInput(text);
      return;
    }

    setInput("[File uploaded: " + file.name + "] PDF/DOCX extraction requires backend service.");
  }

  // Image → OCR placeholder
  function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setImagePreview(url);
    setInput("[OCR placeholder] Connect OCR API to extract text from image.");
  }

  return (
    <div className="app-bg min-h-screen flex items-center justify-center p-6">
      <div className="glass-card center-max p-6">
        <div className="flex items-center justify-between mb-4">
          <Link to="/" className="inline-flex items-center gap-2 text-sm text-gray-600">
            <ArrowLeft size={16} /> Back
          </Link>
          <h2 className="font-bold text-lg">Translation Tool</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Side */}
          <div>
            {/* Source Language */}
            <label className="font-semibold">Source Language</label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full p-2 rounded border mt-2"
            >
              {LANGS.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>

            {/* Target Language */}
            <label className="font-semibold mt-4 block">Target Language</label>
            <select
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              className="w-full p-2 rounded border mt-2"
            >
              {LANGS.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>

            {/* Text Input */}
            <label className="font-semibold mt-4 block">Text to Translate</label>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              rows={8}
              className="w-full p-4 mt-2 rounded-lg"
            />

            {/* File Upload */}
            <div className="mt-4">
              <label className="font-semibold block">Upload Text/PDF/DOCX</label>
              <div className="mt-2 flex items-center gap-2">
                <label className="cursor-pointer px-4 py-2 rounded bg-indigo-600 text-white inline-flex items-center gap-2">
                  <Upload size={16} /> Upload File
                  <input type="file" className="hidden" onChange={handleFileUpload} />
                </label>
                {fileName && <span className="text-sm text-gray-700">{fileName}</span>}
              </div>
            </div>

            {/* Image Upload */}
            <div className="mt-4">
              <label className="font-semibold block">Upload Image (OCR)</label>
              <div className="mt-2 flex items-center gap-2">
                <label className="cursor-pointer px-4 py-2 rounded bg-green-600 text-white inline-flex items-center gap-2">
                  <Upload size={16} /> Upload Image
                  <input type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
                </label>
              </div>

              {imagePreview && (
                <img
                  src={imagePreview}
                  alt="Uploaded preview"
                  className="w-32 h-32 object-cover mt-3 rounded-lg border"
                />
              )}
            </div>

            <div className="mt-4 flex gap-2">
              <button onClick={translate} className="px-4 py-2 rounded bg-indigo-600 text-white">
                Translate
              </button>
              <button
                onClick={() => {
                  setInput("");
                  setOutput("");
                  setImagePreview(null);
                  setFileName(null);
                }}
                className="px-4 py-2 rounded border"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Right Side */}
          <div>
            <label className="font-semibold">Translation Result</label>
            <div className="p-4 mt-2 rounded-lg bg-white/60 min-h-[300px] whitespace-pre-wrap">
              {output || <div className="text-gray-500">No translation yet — click Translate.</div>}
            </div>

            <div className="text-xs text-gray-600 mt-3">
              * For real translations: connect to a backend (Google Translate / Azure / AWS / LibreTranslate)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
