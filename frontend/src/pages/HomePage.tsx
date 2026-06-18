import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, Note } from "../api/client";
import NoteCard from "../components/NoteCard";
import { useWebSocket } from "../hooks/useWebSocket";
import { restoreListScroll, saveListScroll } from "../hooks/useListScrollRestore";

export default function HomePage() {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);

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

  useEffect(() => {
    if (!loading && notes.length > 0) {
      restoreListScroll();
    }
  }, [loading, notes.length]);

  useWebSocket((event, data) => {
    if (["note_created", "note_updated", "note_restored"].includes(event)) {
      load();
    }
    if (["note_archived", "note_trashed", "note_deleted"].includes(event)) {
      setNotes((prev) => prev.filter((n) => n.id !== (data as { id: string }).id));
    }
  });

  const openNote = (note: Note) => {
    saveListScroll(note.id);
    navigate(`/notes/${note.id}`);
  };

  return (
    <div>
      {loading ? (
        <p className="text-center text-muted text-sm py-8">لوڈ ہو رہا ہے...</p>
      ) : notes.length === 0 ? (
        <p className="text-center text-muted text-sm py-8">کوئی نوٹ نہیں ملا</p>
      ) : (
        <div className="grid gap-3 sm:gap-4 md:grid-cols-2 xl:grid-cols-3">
          {notes.map((note) => (
            <NoteCard key={note.id} note={note} onClick={() => openNote(note)} />
          ))}
        </div>
      )}

      <button type="button" className="fab" onClick={() => navigate("/notes/new")} aria-label="نیا نوٹ">
        +
      </button>
    </div>
  );
}
