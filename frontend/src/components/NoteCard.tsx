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
      onClick={onClick}
      className="bg-section rounded-card p-4 cursor-pointer border-r-[5px] border-primary hover:shadow-md transition-shadow"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick()}
    >
      <h2 className="font-title text-primary text-xl mb-2">{note.display_title}</h2>
      <p className="text-base line-clamp-3 text-gray-700">{lines}</p>
      {note.categories.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {note.categories.map((c) => (
            <span key={c.id} className="text-sm bg-badge text-primary px-2 py-0.5 rounded-full">
              {c.name}
            </span>
          ))}
        </div>
      )}
      {note.author_name && (
        <p className="text-sm text-primary mt-2">تحریر از: {note.author_name}</p>
      )}
    </article>
  );
}
