import React, { useState } from "react";
import { ArrowLeft, Upload } from "lucide-react";
import { Link } from "react-router-dom";

function summarizeText(text) {
  const sents = text.match(/[^\.\!?]+[\.\!?]+/g) || [text];
  if (sents.length <= 3) return sents.join(" ").trim();
  return sents.slice(0, 3).join(" ").trim();
}

export default function Summarization() {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");
  const [isReading, setIsReading] = useState(false);
  const [fileName, setFileName] = useState("");

  function handleSummarize() {
    const s = summarizeText(text);
    setSummary(s);
  }

  function readSummary() {
    if (!("speechSynthesis" in window) || !summary) {
      alert("No summary or TTS not supported.");
      return;
    }
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(summary);
    u.onend = () => setIsReading(false);
    setIsReading(true);
    window.speechSynthesis.speak(u);
  }

  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(file.name);

    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = async () => {
        setText("Extracting text...");
        setSummary("");
      };
      reader.readAsDataURL(file);
    } else {
      const reader = new FileReader();
      reader.onload = () => {
        setText(reader.result);
      };
      reader.readAsText(file);
    }
  }

  return (
    <div className="app-bg min-h-screen flex items-center justify-center p-6">
      <div className="glass-card center-max p-6">
        <div className="flex items-center justify-between mb-4">
          <Link to="/" className="inline-flex items-center gap-2 text-sm text-gray-600">
            <ArrowLeft size={16} /> Back
          </Link>
          <h2 className="font-bold text-lg">Summarization</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <label className="font-semibold">Input text or file</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={12}
              className="w-full p-4 mt-2 rounded-lg"
              placeholder="Paste text or upload a file..."
            />

            <div className="mt-3 flex flex-col gap-3">
              <label className="cursor-pointer flex items-center gap-2 bg-gray-200 px-3 py-2 rounded-lg w-fit">
                <Upload size={18} />
                <span>{fileName || "Upload file (PDF, TXT, DOCX, Images)"}</span>
                <input type="file" className="hidden" onChange={handleFileUpload} />
              </label>

              <div className="flex gap-2">
                <button onClick={handleSummarize} className="px-4 py-2 rounded bg-indigo-600 text-white">
                  Summarize
                </button>
                <button
                  onClick={() => {
                    setText("");
                    setSummary("");
                    setFileName("");
                  }}
                  className="px-4 py-2 rounded border"
                >
                  Clear
                </button>
              </div>
            </div>
          </div>

          <div>
            <label className="font-semibold">Summary</label>
            <div className="p-4 mt-2 rounded-lg bg-white/60 min-h-[200px]">
              {summary || <div className="text-gray-500">No summary yet — click Summarize.</div>}
              <div className="mt-4 flex gap-2">
                <button
                  onClick={readSummary}
                  disabled={!summary || isReading}
                  className="px-4 py-2 rounded bg-green-600 text-white"
                >
                  Read Summary
                </button>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(summary);
                    alert("Copied");
                  }}
                  disabled={!summary}
                  className="px-4 py-2 rounded border"
                >
                  Copy
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}