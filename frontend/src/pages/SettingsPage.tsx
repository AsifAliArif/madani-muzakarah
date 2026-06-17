import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function SettingsPage() {
  const [llmName, setLlmName] = useState("gemini-1.5-flash");
  const [apiKey, setApiKey] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [hasKey, setHasKey] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.admin.aiSettings().then((s) => {
      setLlmName(s.llm_name);
      setSystemPrompt(s.system_prompt);
      setHasKey(s.has_api_key);
    });
  }, []);

  const save = async () => {
    await api.admin.updateAiSettings({
      llm_name: llmName,
      api_key: apiKey || undefined,
      system_prompt: systemPrompt,
    });
    setSaved(true);
    setApiKey("");
    setHasKey(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-3xl">
      <h2 className="font-title text-2xl text-primary mb-6">AI سیٹنگز</h2>
      <div className="space-y-4">
        <div>
          <label className="block mb-2 text-primary">LLM نام</label>
          <input
            type="text"
            value={llmName}
            onChange={(e) => setLlmName(e.target.value)}
            placeholder="gemini-1.5-flash یا gpt-4o"
            className="w-full border rounded-lg px-4 py-2"
          />
        </div>
        <div>
          <label className="block mb-2 text-primary">API Key {hasKey && <span className="text-green-600 text-sm">(محفوظ ہے)</span>}</label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder={hasKey ? "تبدیلی کے لیے نئی key درج کریں" : "API Key"}
            className="w-full border rounded-lg px-4 py-2"
          />
        </div>
        <div>
          <label className="block mb-2 text-primary">سسٹم پرامپٹ</label>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            rows={12}
            className="w-full border rounded-lg px-4 py-2 font-mono text-sm"
            dir="ltr"
          />
        </div>
        <button type="button" onClick={save} className="px-6 py-2 bg-accent text-white rounded-full min-h-[44px]">
          محفوظ کریں
        </button>
        {saved && <p className="text-green-600">محفوظ ہو گیا!</p>}
      </div>
    </div>
  );
}
