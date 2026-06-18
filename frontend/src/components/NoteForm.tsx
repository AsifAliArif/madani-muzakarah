import { useState } from "react";
import { useNavigate } from "react-router-dom";
import TipTapEditor from "../editor/TipTapEditor";
import CategoryPicker from "./CategoryPicker";
import ActionButton from "./ActionButton";
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
        <label className="block text-primary font-title mb-1.5 text-base">ہیڈنگ (اختیاری)</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="خالی چھوڑیں تو پہلی لائن ہیڈنگ بنے گی"
          className="w-full border border-gray-200 rounded-lg px-3 py-2 font-title text-base focus:border-primary focus:outline-none"
        />
      </div>

      <div>
        <label className="block text-primary font-title mb-1.5 text-base">مرکزی مواد</label>
        <TipTapEditor content={content} onChange={setContent} />
      </div>

      <CategoryPicker selected={categories} onChange={setCategories} />

      <div>
        <label className="block text-primary font-title mb-1.5 text-base">تحریر از:</label>
        <input
          type="text"
          value={authorName}
          onChange={(e) => setAuthorName(e.target.value)}
          placeholder="اپنا نام لکھیں"
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-base focus:border-primary focus:outline-none"
        />
      </div>

      {error && <p className="text-red-600">{error}</p>}

      <div className="flex gap-2 flex-wrap pt-2">
        <ActionButton variant="accent" onClick={save} disabled={saving}>
          {saving ? "..." : "محفوظ"}
        </ActionButton>
        <ActionButton variant="outline" onClick={onCancel}>منسوخ</ActionButton>
      </div>
    </div>
  );
}
