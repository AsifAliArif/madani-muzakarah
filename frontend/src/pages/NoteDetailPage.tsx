import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, Note } from "../api/client";
import NoteForm from "../components/NoteForm";
import ExportMenu from "../components/ExportMenu";
import { useAuth } from "../hooks/useAuth";

export default function NoteDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [note, setNote] = useState<Note | null>(null);
  const [editing, setEditing] = useState(id === "new");
  const [loading, setLoading] = useState(id !== "new");

  useEffect(() => {
    if (id === "new") return;
    setLoading(true);
    api.notes.get(id!).then(setNote).catch(() => navigate("/")).finally(() => setLoading(false));
  }, [id, navigate]);

  if (id === "new") {
    return (
      <div>
        <h2 className="font-title text-2xl text-primary mb-6">نیا نوٹ</h2>
        <NoteForm onSaved={() => navigate("/")} onCancel={() => navigate("/")} />
      </div>
    );
  }

  if (loading) return <p>لوڈ ہو رہا ہے...</p>;
  if (!note) return null;

  if (editing) {
    return (
      <div>
        <h2 className="font-title text-2xl text-primary mb-6">نوٹ میں ترمیم</h2>
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
      <header className="mb-6">
        <h1 className="font-title text-3xl text-primary mb-2">{note.display_title}</h1>
        {note.author_name && (
          <p className="text-primary text-lg">تحریر از: {note.author_name}</p>
        )}
        {note.categories.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {note.categories.map((c) => (
              <span key={c.id} className="bg-badge text-primary px-3 py-1 rounded-full text-sm">{c.name}</span>
            ))}
          </div>
        )}
      </header>

      <div className="note-content bg-white rounded-card p-6 border mb-6" dangerouslySetInnerHTML={{ __html: note.content_html }} />

      <ExportMenu title={note.display_title} contentHtml={note.content_html} authorName={note.author_name} />

      <div className="flex flex-wrap gap-3 mt-6">
        <button type="button" onClick={() => setEditing(true)} className="px-4 py-2 bg-primary text-white rounded-full min-h-[44px]">
          ترمیم
        </button>
        <button type="button" onClick={handleArchive} className="px-4 py-2 border border-primary text-primary rounded-full min-h-[44px]">
          آرکائیو
        </button>
        <button type="button" onClick={handleTrash} className="px-4 py-2 border border-red-500 text-red-600 rounded-full min-h-[44px]">
          ڈیلیٹ
        </button>
        {isAdmin && note.status === "trashed" && (
          <>
            <button type="button" onClick={async () => { await api.notes.restore(note.id); navigate("/"); }} className="px-4 py-2 bg-accent text-white rounded-full">
              بحال کریں
            </button>
            <button type="button" onClick={async () => { if (confirm("ہمیشہ کے لیے حذف؟")) { await api.notes.deleteForever(note.id); navigate("/admin/trash"); } }} className="px-4 py-2 bg-red-600 text-white rounded-full">
              ہمیشہ کے لیے حذف
            </button>
          </>
        )}
      </div>
    </article>
  );
}
