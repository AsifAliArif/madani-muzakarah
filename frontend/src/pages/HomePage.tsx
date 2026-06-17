import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, Note } from "../api/client";
import NoteCard from "../components/NoteCard";
import { useWebSocket } from "../hooks/useWebSocket";

export default function HomePage() {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [term2, setTerm2] = useState("");
  const [mode, setMode] = useState("broad");
  const [searching, setSearching] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.notes.list("active");
      setNotes(data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  useWebSocket((event, data) => {
    if (["note_created", "note_updated", "note_restored"].includes(event)) {
      load();
    }
    if (["note_archived", "note_trashed", "note_deleted"].includes(event)) {
      setNotes((prev) => prev.filter((n) => n.id !== (data as { id: string }).id));
    }
  });

  const doSearch = useCallback(async () => {
    if (!query && !term2) {
      const data = await api.notes.list("active");
      setNotes(data);
      return;
    }
    setSearching(true);
    try {
      const terms = term2 ? [term2] : [];
      const result = await api.notes.search({ query, mode, terms });
      setNotes(result.notes);
    } finally {
      setSearching(false);
    }
  }, [query, term2, mode]);

  useEffect(() => {
    const t = setTimeout(() => { doSearch(); }, 400);
    return () => clearTimeout(t);
  }, [doSearch]);

  return (
    <div>
      <div className="bg-section rounded-card p-4 mb-6">
        <h2 className="font-title text-primary text-2xl mb-4">نوٹس تلاش کریں</h2>
        <div className="grid gap-3 md:grid-cols-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="تلاش..."
            className="border rounded-lg px-4 py-2"
          />
          <input
            type="text"
            value={term2}
            onChange={(e) => setTerm2(e.target.value)}
            placeholder="دوسرا لفظ (اختیاری)"
            className="border rounded-lg px-4 py-2"
          />
          <select value={mode} onChange={(e) => setMode(e.target.value)} className="border rounded-lg px-4 py-2">
            <option value="broad">وسیع تلاش</option>
            <option value="word">لفظی</option>
            <option value="phrase">جملہ</option>
            <option value="exact">ہوبہو</option>
          </select>
        </div>
      </div>

      {loading || searching ? (
        <p className="text-center text-gray-500">لوڈ ہو رہا ہے...</p>
      ) : notes.length === 0 ? (
        <p className="text-center text-gray-500">کوئی نوٹ نہیں ملا</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {notes.map((note) => (
            <NoteCard key={note.id} note={note} onClick={() => navigate(`/notes/${note.id}`)} />
          ))}
        </div>
      )}

      <button type="button" className="fab" onClick={() => navigate("/notes/new")} aria-label="نیا نوٹ">
        +
      </button>
    </div>
  );
}
