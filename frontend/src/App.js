// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { BookOpen, Volume2, FileText, Globe } from "lucide-react";
import DyslexiaFont from "./pages/DyslexiaFont";
import TextToSpeech from "./pages/TextToSpeech";
import Summarization from "./pages/Summarization";
import TranslationTool from "./pages/TranslationTool";
import "./index.css";

function HomePage() {
  const tools = [
    { name: "Dyslexia Font", path: "/dyslexia-font", icon: <BookOpen size={36} /> },
    { name: "Text to Speech", path: "/text-to-speech", icon: <Volume2 size={36} /> },
    { name: "Summarization", path: "/summarization", icon: <FileText size={36} /> },
    { name: "Translation", path: "/translation", icon: <Globe size={36} /> },
  ];

  return (
    <div className="app-bg min-h-screen flex items-center justify-center p-6">
      <div className="glass-card center-max p-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Accessibility Tools</h1>
            <p className="text-sm text-gray-600 mt-1">Dyslexia-friendly reader • TTS • Summaries • Translation</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {tools.map((t) => (
            <Link
              to={t.path}
              key={t.name}
              className="flex flex-col items-center justify-center gap-3 p-6 rounded-xl bg-white/60 hover:scale-105 transition transform shadow"
            >
              <div className="text-indigo-600">{t.icon}</div>
              <div className="font-semibold">{t.name}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dyslexia-font" element={<DyslexiaFont />} />
        <Route path="/text-to-speech" element={<TextToSpeech />} />
        <Route path="/summarization" element={<Summarization />} />
        <Route path="/translation" element={<TranslationTool />} />
      </Routes>
    </Router>
  );
}
