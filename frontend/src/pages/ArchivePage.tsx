import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, Note } from "../api/client";
import NoteCard from "../components/NoteCard";
import { saveListScroll } from "../hooks/useListScrollRestore";

export default function ArchivePage() {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<Note[]>([]);

  useEffect(() => {
    api.notes.list("archived").then(setNotes);
  }, []);

  return (
    <div>
      <h2 className="font-title text-xl text-primary mb-4">آرکائیو نوٹس</h2>
      {notes.length === 0 ? (
        <p className="text-muted text-sm">آرکائیو خالی ہے</p>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {notes.map((note) => (
            <NoteCard
              key={note.id}
              note={note}
              onClick={() => { saveListScroll(note.id); navigate(`/notes/${note.id}`); }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
