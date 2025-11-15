import React, { useState, useRef, useEffect } from "react";
import { FiFileText, FiVolume2, FiGlobe, FiPlay, FiPause, FiRotateCw } from "react-icons/fi";

// Single-file React component using TailwindCSS classes.
// Requirements: install react-icons and Tailwind in your project.
// npm install react-icons
// Tailwind setup: https://tailwindcss.com/docs/guides/create-react-app (or your framework)

export default function DyslexiaAccessibilityUI() {
  const [inputText, setInputText] = useState(
    `This is a sample paragraph. It demonstrates how summarization and reading aids help dyslexic and visually impaired users. Use the controls to increase font size, change spacing, or enable a dyslexia-friendly font. Try the text-to-speech button to hear the content.`
  );

  const [summary, setSummary] = useState("");
  const [fontSize, setFontSize] = useState(18);
  const [lineHeight, setLineHeight] = useState(1.8);
  const [letterSpacing, setLetterSpacing] = useState(0.5);
  const [fontFamily, setFontFamily] = useState("system");
  const [highContrast, setHighContrast] = useState(false);
  const [ttsPlaying, setTtsPlaying] = useState(false);
  const [voiceRate, setVoiceRate] = useState(1);
  const [voicePitch, setVoicePitch] = useState(1);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [voices, setVoices] = useState([]);
  const [targetLang, setTargetLang] = useState("en");
  const speechUtterRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    // load available voices
    function loadVoices() {
      const v = window.speechSynthesis.getVoices();
      setVoices(v);
      if (v.length && !selectedVoice) setSelectedVoice(v[0]?.name);
    }
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);

  function simpleSummarize(text, maxSentences = 3) {
    // Very simple summarizer: split on sentence enders and take first N non-empty sentences.
    const sentences = text
      .replace(/\n+/g, " ")
      .split(/(?<=[.!?])\s+/)
      .map((s) => s.trim())
      .filter(Boolean);
    return sentences.slice(0, maxSentences).join(" ");
  }

  function handleSummarize() {
    const s = simpleSummarize(inputText, 3);
    setSummary(s || "(No summary produced.)");
  }

  function handleResetControls() {
    setFontSize(18);
    setLineHeight(1.8);
    setLetterSpacing(0.5);
    setFontFamily("system");
    setHighContrast(false);
  }

  function speak(text) {
    if (!window.speechSynthesis) return alert("Text-to-speech is not supported in this browser.");
    // stop any existing
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    const voice = voices.find((v) => v.name === selectedVoice);
    if (voice) utter.voice = voice;
    utter.rate = voiceRate;
    utter.pitch = voicePitch;
    utter.onend = () => setTtsPlaying(false);
    speechUtterRef.current = utter;
    setTtsPlaying(true);
    window.speechSynthesis.speak(utter);
  }

  function stopSpeak() {
    window.speechSynthesis.cancel();
    setTtsPlaying(false);
  }

  function handleTranslate(text, target) {
    // Demo translation: for a real app, wire to a translation API (Google Translate, DeepL, Azure Translator, etc.)
    // Here we just return a placeholder so the UI can be tested without server calls.
    if (target === "en") return Promise.resolve(text);
    return Promise.resolve(text + ` \n\n[Translated to ${target.toUpperCase()} — replace this with a real API call]`);
  }

  async function handleTranslateAndSet() {
    const translated = await handleTranslate(inputText, targetLang);
    setInputText(translated);
    setSummary("");
  }

  // helper classes
  const containerBg = highContrast ? "bg-black text-white" : "bg-white text-gray-900";
  const cardBg = highContrast ? "bg-yellow-500 text-black" : "bg-white";

  // font family mapping
  const fontMap = {
    system: "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial",
    serif: "Georgia, 'Times New Roman', Times, serif",
    dyslexic: "'OpenDyslexic', 'Fira Sans', Arial, sans-serif",
  };

  return (
    <div className={`min-h-screen py-8 px-6 ${containerBg}`}>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-extrabold tracking-tight">Text Accessibility Suite</h1>
          <nav className="flex gap-4 items-center">
            <button
              className="text-sm px-3 py-2 rounded-md border"
              onClick={() => {
                textareaRef.current?.focus();
              }}
            >
              Focus text
            </button>
            <button
              className="text-sm px-3 py-2 rounded-md border"
              onClick={() => {
                // toggle contrast
                setHighContrast((s) => !s);
              }}
            >
              Toggle high contrast
            </button>
          </nav>
        </header>

        {/* Services row */}
        <section aria-labelledby="services-heading" className="mb-12">
          <h2 id="services-heading" className="text-4xl text-center font-bold mb-2">
            SERVICES
          </h2>
          <p className="text-center italic mb-8">Providing tools for dyslexic and visually impaired readers</p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
            <article className="flex flex-col items-center text-center p-6">
              <div className="rounded-full p-6 bg-yellow-400 text-white mb-4">
                <FiFileText size={48} />
              </div>
              <h3 className="text-2xl font-semibold mb-2">Summarization</h3>
              <p className="max-w-sm">Quickly condense long text into short, readable summaries to reduce cognitive load.</p>
            </article>

            <article className="flex flex-col items-center text-center p-6">
              <div className="rounded-full p-6 bg-yellow-400 text-white mb-4">
                <FiVolume2 size={48} />
              </div>
              <h3 className="text-2xl font-semibold mb-2">Text to Speech</h3>
              <p className="max-w-sm">Listen to content with configurable voice rate, pitch, and voice selection.</p>
            </article>

            <article className="flex flex-col items-center text-center p-6">
              <div className="rounded-full p-6 bg-yellow-400 text-white mb-4">
                <FiGlobe size={48} />
              </div>
              <h3 className="text-2xl font-semibold mb-2">Translation</h3>
              <p className="max-w-sm">Translate content into a supported language — connect a translation API for production use.</p>
            </article>
          </div>
        </section>

        {/* Control panel + Editor */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 p-6 rounded-lg border" style={{ backgroundColor: highContrast ? "#000" : "#fff" }}>
            <label className="block text-sm font-medium mb-2">Input text</label>
            <textarea
              ref={textareaRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              rows={9}
              aria-label="Text to summarize and read"
              className="w-full p-4 rounded-md shadow-sm border resize-none"
              style={{
                fontSize: `${fontSize}px`,
                lineHeight: lineHeight,
                letterSpacing: `${letterSpacing}px`,
                fontFamily: fontMap[fontFamily],
                backgroundColor: highContrast ? "#000" : "#fff",
                color: highContrast ? "#fff" : "inherit",
              }}
            />

            <div className="mt-4 flex flex-wrap gap-3 items-center">
              <button
                className="px-4 py-2 rounded-md bg-yellow-400 text-black font-semibold"
                onClick={handleSummarize}
              >
                Summarize
              </button>

              <button
                className="px-4 py-2 rounded-md bg-yellow-400 text-black font-semibold flex items-center gap-2"
                onClick={() => (ttsPlaying ? stopSpeak() : speak(inputText))}
                aria-pressed={ttsPlaying}
              >
                {ttsPlaying ? <FiPause /> : <FiPlay />} {ttsPlaying ? "Stop" : "Read"}
              </button>

              <select
                value={selectedVoice || ""}
                onChange={(e) => setSelectedVoice(e.target.value)}
                aria-label="Select voice"
                className="px-3 py-2 border rounded-md"
              >
                {voices.length === 0 ? (
                  <option>Loading voices...</option>
                ) : (
                  voices.map((v) => (
                    <option key={v.name} value={v.name}>
                      {v.name} {v.lang ? `(${v.lang})` : ""}
                    </option>
                  ))
                )}
              </select>

              <button
                className="px-3 py-2 border rounded-md"
                onClick={() => {
                  // copy text
                  navigator.clipboard?.writeText(inputText);
                }}
              >
                Copy
              </button>

              <button
                className="px-3 py-2 border rounded-md"
                onClick={() => {
                  setInputText("");
                  setSummary("");
                }}
              >
                Clear
              </button>
            </div>

            {/* Summary output */}
            <div className="mt-6">
              <h4 className="text-lg font-semibold mb-2">Summary</h4>
              <div
                className="p-4 border rounded-md min-h-[80px]"
                style={{ fontSize: `${Math.max(16, fontSize - 2)}px`, lineHeight }}
              >
                {summary || <em>No summary yet — click Summarize.</em>}
              </div>
            </div>
          </div>

          {/* Right column: reading aids controls */}
          <aside className="p-6 rounded-lg border">
            <h4 className="text-lg font-semibold mb-3">Reading Aids</h4>

            <label className="block text-sm mb-1">Font size: {fontSize}px</label>
            <input
              type="range"
              min={12}
              max={36}
              value={fontSize}
              onChange={(e) => setFontSize(Number(e.target.value))}
              className="w-full mb-3"
            />

            <label className="block text-sm mb-1">Line height: {lineHeight}</label>
            <input
              type="range"
              min={1}
              max={2.6}
              step={0.1}
              value={lineHeight}
              onChange={(e) => setLineHeight(Number(e.target.value))}
              className="w-full mb-3"
            />

            <label className="block text-sm mb-1">Letter spacing: {letterSpacing}px</label>
            <input
              type="range"
              min={0}
              max={2}
              step={0.1}
              value={letterSpacing}
              onChange={(e) => setLetterSpacing(Number(e.target.value))}
              className="w-full mb-3"
            />

            <label className="block text-sm mb-1">Font family</label>
            <select
              value={fontFamily}
              onChange={(e) => setFontFamily(e.target.value)}
              className="w-full mb-3 px-3 py-2 border rounded-md"
            >
              <option value="system">System (sans)</option>
              <option value="serif">Serif</option>
              <option value="dyslexic">Dyslexic-friendly (OpenDyslexic)</option>
            </select>

            <label className="flex items-center gap-2 mb-3">
              <input
                type="checkbox"
                checked={highContrast}
                onChange={(e) => setHighContrast(e.target.checked)}
              />
              High contrast mode
            </label>

            <div className="border-t pt-3 mt-3">
              <h5 className="font-medium mb-2">Text-to-Speech</h5>
              <label className="block text-sm mb-1">Rate: {voiceRate.toFixed(1)}</label>
              <input type="range" min={0.5} max={2} step={0.1} value={voiceRate} onChange={(e) => setVoiceRate(Number(e.target.value))} className="w-full mb-2" />
              <label className="block text-sm mb-1">Pitch: {voicePitch.toFixed(1)}</label>
              <input type="range" min={0.5} max={2} step={0.1} value={voicePitch} onChange={(e) => setVoicePitch(Number(e.target.value))} className="w-full mb-2" />
            </div>

            <div className="border-t pt-3 mt-3">
              <h5 className="font-medium mb-2">Translation (demo)</h5>
              <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)} className="w-full mb-2 px-3 py-2 border rounded-md">
                <option value="en">English</option>
                <option value="hi">Hindi</option>
                <option value="es">Spanish</option>
                <option value="ta">Tamil</option>
                <option value="bn">Bengali</option>
              </select>
              <button className="w-full px-4 py-2 rounded-md bg-yellow-400 text-black font-semibold" onClick={handleTranslateAndSet}>
                Translate (demo)
              </button>
            </div>

            <div className="mt-4 text-sm text-gray-500">
              <p>Tip: For production translation, integrate a translation API and replace the demo function.</p>
            </div>

            <div className="mt-6">
              <button className="px-3 py-2 rounded-md border mr-2" onClick={handleResetControls}>
                Reset controls
              </button>
              <button
                className="px-3 py-2 rounded-md border"
                onClick={() => {
                  // accessibility: scroll textarea into view
                  textareaRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
                }}
              >
                Go to editor
              </button>
            </div>
          </aside>
        </section>

        <footer className="mt-12 text-center text-sm text-gray-500">
          <p>Accessibility-first reading aid prototype — adapt and connect real ML and translation services as needed.</p>
          <p className="mt-2">To enable the OpenDyslexic font, include it in your index.html or import it via CSS.</p>
        </footer>
      </div>
    </div>
  );
}

## Main Dashboard UI (Home Page)
```jsx
import React from "react";
import { FaVolumeUp, FaFont, FaLanguage, FaAlignLeft } from "react-icons/fa";

const ToolCard = ({ icon: Icon, title, onClick }) => (
  <div
    onClick={onClick}
    className="flex flex-col items-center bg-white rounded-2xl shadow-md p-6 cursor-pointer hover:scale-105 transition-transform w-48"
  >
    <Icon size={40} className="mb-4 text-blue-600" />
    <h3 className="text-lg font-semibold text-gray-800 text-center">{title}</h3>
  </div>
);

const MainDashboard = ({ setActiveTool }) => {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center py-16 px-6">
      <h1 className="text-3xl font-bold mb-10 text-gray-900 text-center">
        Accessibility Tools for Dyslexia & Visual Impairment
      </h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10">
        <ToolCard
          icon={FaVolumeUp}
          title="Text to Speech"
          onClick={() => setActiveTool("tts")}
        />

        <ToolCard
          icon={FaAlignLeft}
          title="Summarization"
          onClick={() => setActiveTool("summarize")}
        />

        <ToolCard
          icon={FaFont}
          title="Dyslexia-Friendly Font"
          onClick={() => setActiveTool("dyslexia")}
        />

        <ToolCard
          icon={FaLanguage}
          title="Translation"
          onClick={() => setActiveTool("translate")}
        />
      </div>
    </div>
  );
};

export default MainDashboard;
```

