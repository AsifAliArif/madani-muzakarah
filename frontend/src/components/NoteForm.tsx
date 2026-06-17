import { useState } from "react";
import { useNavigate } from "react-router-dom";
import TipTapEditor from "../editor/TipTapEditor";
import CategoryPicker from "./CategoryPicker";
import { api, Note } from "../api/client";

interface Props {
  note?: Note;
  onSaved: () => void;
  onCancel: () => void;
}

export default function NoteForm({ note, onSaved, onCancel }: Props) {
  const navigate = useNavigate();
  const [title, setTitle] = useState(note?.title || "");
  const [content, setContent] = useState(note?.content_html || "");
  const [authorName, setAuthorName] = useState(note?.author_name || "");
  const [categories, setCategories] = useState<string[]>(note?.categories.map((c) => c.name) || []);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const save = async () => {
    setSaving(true);
    setError("");
    try {
      const payload = {
        title: title.trim() || null,
        content_html: content,
        author_name: authorName,
        category_names: categories,
      };
      if (note) {
        const updated = await api.notes.update(note.id, payload);
        navigate(`/notes/${updated.id}`);
      } else {
        const created = await api.notes.create(payload);
        navigate(`/notes/${created.id}`);
      }
      onSaved();
    } catch (e) {
      setError(e instanceof Error ? e.message : "محفوظ نہیں ہوا");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      <div>
        <label className="block text-primary font-title mb-2">ہیڈنگ (اختیاری)</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="خالی چھوڑیں تو پہلی لائن ہیڈنگ بنے گی"
          className="w-full border border-gray-300 rounded-lg px-4 py-2 font-title text-lg"
        />
      </div>

      <div>
        <label className="block text-primary font-title mb-2">مرکزی مواد</label>
        <TipTapEditor content={content} onChange={setContent} />
      </div>

      <CategoryPicker selected={categories} onChange={setCategories} />

      <div>
        <label className="block text-primary font-title mb-2">تحریر از:</label>
        <input
          type="text"
          value={authorName}
          onChange={(e) => setAuthorName(e.target.value)}
          placeholder="اپنا نام لکھیں"
          className="w-full border border-gray-300 rounded-lg px-4 py-2"
        />
      </div>

      {error && <p className="text-red-600">{error}</p>}

      <div className="flex gap-3 flex-wrap">
        <button type="button" onClick={save} disabled={saving} className="px-6 py-2 bg-accent text-white rounded-full min-h-[44px] disabled:opacity-50">
          {saving ? "محفوظ ہو رہا ہے..." : "محفوظ کریں"}
        </button>
        <button type="button" onClick={onCancel} className="px-6 py-2 border border-primary text-primary rounded-full min-h-[44px]">
          منسوخ
        </button>
      </div>
    </div>
  );
}
