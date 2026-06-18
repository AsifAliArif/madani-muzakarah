import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, Note } from "../api/client";
import NoteForm from "../components/NoteForm";
import ExportMenu from "../components/ExportMenu";
import ActionButton from "../components/ActionButton";
import { useAuth } from "../hooks/useAuth";

const FONT_SCALES = [0.85, 1, 1.15, 1.3];

export default function NoteDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [note, setNote] = useState<Note | null>(null);
  const [editing, setEditing] = useState(id === "new");
  const [loading, setLoading] = useState(id !== "new");
  const [fontScaleIdx, setFontScaleIdx] = useState(1);

  useEffect(() => {
    document.documentElement.style.setProperty("--note-font-scale", String(FONT_SCALES[fontScaleIdx]));
    return () => {
      document.documentElement.style.removeProperty("--note-font-scale");
    };
  }, [fontScaleIdx]);

  useEffect(() => {
    if (id === "new") return;
    setLoading(true);
    api.notes.get(id!).then(setNote).catch(() => navigate("/")).finally(() => setLoading(false));
  }, [id, navigate]);

  const handleBack = () => navigate("/");

  if (id === "new") {
    return (
      <div>
        <button type="button" className="back-btn" onClick={handleBack} aria-label="واپس">
          →
        </button>
        <h2 className="font-title text-xl text-primary mb-4">نیا نوٹ</h2>
        <NoteForm onSaved={() => navigate("/")} onCancel={() => navigate("/")} />
      </div>
    );
  }

  if (loading) return <p className="text-muted text-sm">لوڈ ہو رہا ہے...</p>;
  if (!note) return null;

  if (editing) {
    return (
      <div>
        <button type="button" className="back-btn" onClick={() => setEditing(false)} aria-label="واپس">
          →
        </button>
        <h2 className="font-title text-xl text-primary mb-4">نوٹ میں ترمیم</h2>
        <NoteForm
          note={note}
          onSaved={() => { setEditing(false); api.notes.get(note.id).then(setNote); }}
          onCancel={() => setEditing(false)}
        />
      </div>
    );
  }

  const handleArchive = async () => {
    await api.notes.archive(note.id);
    navigate("/archive");
  };

  const handleTrash = async () => {
    if (confirm("کیا آپ اس نوٹ کو ڈیلیٹ کرنا چاہتے ہیں؟")) {
      await api.notes.trash(note.id);
      navigate("/");
    }
  };

  return (
    <article className="max-w-4xl mx-auto">
      <button type="button" className="back-btn" onClick={handleBack} aria-label="واپس">
        →
      </button>

      <header className="mb-3">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <h1 className="note-detail-title flex-1">{note.display_title}</h1>
          <div className="font-size-controls">
            <button
              type="button"
              className="font-size-btn"
              onClick={() => setFontScaleIdx((i) => Math.max(0, i - 1))}
              disabled={fontScaleIdx === 0}
              aria-label="فونٹ چھوٹا"
            >
              −
            </button>
            <button
              type="button"
              className="font-size-btn"
              onClick={() => setFontScaleIdx((i) => Math.min(FONT_SCALES.length - 1, i + 1))}
              disabled={fontScaleIdx === FONT_SCALES.length - 1}
              aria-label="فونٹ بڑا"
            >
              +
            </button>
          </div>
        </div>
        {note.categories.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {note.categories.map((c) => (
              <span key={c.id} className="bg-badge text-primary px-2.5 py-0.5 rounded-full text-xs">{c.name}</span>
            ))}
          </div>
        )}
      </header>

      <div
        className="note-content bg-white rounded-card p-4 sm:p-5 border border-primary/10 shadow-card"
        dangerouslySetInnerHTML={{ __html: note.content_html }}
      />

      {note.author_name && (
        <p className="note-author-line">تحریر از: {note.author_name}</p>
      )}

      <div className="mt-4">
        <ExportMenu title={note.display_title} contentHtml={note.content_html} authorName={note.author_name} />
      </div>

      <div className="flex flex-wrap gap-2 mt-4">
        <ActionButton variant="primary" onClick={() => setEditing(true)}>ترمیم</ActionButton>
        <ActionButton variant="outline" onClick={handleArchive}>آرکائیو</ActionButton>
        <ActionButton variant="danger" onClick={handleTrash}>ڈیلیٹ</ActionButton>
        {isAdmin && note.status === "trashed" && (
          <>
            <ActionButton variant="accent" onClick={async () => { await api.notes.restore(note.id); navigate("/"); }}>
              بحال
            </ActionButton>
            <ActionButton
              variant="danger"
              onClick={async () => {
                if (confirm("ہمیشہ کے لیے حذف؟")) {
                  await api.notes.deleteForever(note.id);
                  navigate("/admin/trash");
                }
              }}
            >
              مستقل حذف
            </ActionButton>
          </>
        )}
      </div>
    </article>
  );
}
