import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, Note } from "../api/client";
import NoteCard from "../components/NoteCard";

export default function TrashPage() {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<Note[]>([]);

  useEffect(() => {
    api.notes.list("trashed").then(setNotes);
  }, []);

  const restore = async (id: string) => {
    await api.notes.restore(id);
    setNotes((prev) => prev.filter((n) => n.id !== id));
  };

  const deleteForever = async (id: string) => {
    if (confirm("ہمیشہ کے لیے حذف؟")) {
      await api.notes.deleteForever(id);
      setNotes((prev) => prev.filter((n) => n.id !== id));
    }
  };

  return (
    <div>
      <h2 className="font-title text-2xl text-primary mb-6">ٹریش</h2>
      {notes.length === 0 ? (
        <p className="text-gray-500">ٹریش خالی ہے</p>
      ) : (
        <div className="space-y-4">
          {notes.map((note) => (
            <div key={note.id} className="relative">
              <NoteCard note={note} onClick={() => navigate(`/notes/${note.id}`)} />
              <div className="flex gap-2 mt-2">
                <button type="button" onClick={() => restore(note.id)} className="px-4 py-2 bg-accent text-white rounded-full text-sm">
                  بحال کریں
                </button>
                <button type="button" onClick={() => deleteForever(note.id)} className="px-4 py-2 bg-red-600 text-white rounded-full text-sm">
                  ہمیشہ کے لیے حذف
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
