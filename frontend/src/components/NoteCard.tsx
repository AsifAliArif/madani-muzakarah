import { Note } from "../api/client";
import { stripHtml } from "../export/noteExport";

interface Props {
  note: Note;
  onClick: () => void;
}

export default function NoteCard({ note, onClick }: Props) {
  const preview = note.content_plain || stripHtml(note.content_html);
  const lines = preview.split("\n").filter(Boolean).slice(0, 3).join(" ");

  return (
    <article
      id={`note-${note.id}`}
      onClick={onClick}
      className="note-card"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick()}
    >
      <h2 className="note-card-title">{note.display_title}</h2>
      <p className="note-card-preview line-clamp-3">{lines}</p>
      {note.categories.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-2">
          {note.categories.map((c) => (
            <span key={c.id} className="text-xs bg-badge text-primary px-2 py-0.5 rounded-full">
              {c.name}
            </span>
          ))}
        </div>
      )}
    </article>
  );
}
