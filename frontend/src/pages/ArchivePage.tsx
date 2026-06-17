import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, Note } from "../api/client";
import NoteCard from "../components/NoteCard";

export default function ArchivePage() {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<Note[]>([]);

  useEffect(() => {
    api.notes.list("archived").then(setNotes);
  }, []);

  return (
    <div>
      <h2 className="font-title text-2xl text-primary mb-6">آرکائیو نوٹس</h2>
      {notes.length === 0 ? (
        <p className="text-gray-500">آرکائیو خالی ہے</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {notes.map((note) => (
            <NoteCard key={note.id} note={note} onClick={() => navigate(`/notes/${note.id}`)} />
          ))}
        </div>
      )}
    </div>
  );
}
