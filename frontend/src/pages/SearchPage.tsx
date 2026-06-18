import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api, Category, Note } from "../api/client";
import { stripHtml } from "../export/noteExport";
import { saveListScroll } from "../hooks/useListScrollRestore";

type SearchMode = "broad" | "phrase" | "exact" | "word";

const MODES: { id: SearchMode; label: string; hint: string }[] = [
  { id: "broad", label: "آسان سرچ", hint: "ملتے جلتے الفاظ اور وسیع تلاش" },
  { id: "phrase", label: "سنگل پیج سرچ", hint: "مکمل جملے یا عبارت کی تلاش" },
  { id: "exact", label: "بالکل موافق", hint: "ہوبہو درست مطابقت" },
  { id: "word", label: "لفظی سرچ", hint: "تمام الفاظ موجود ہوں" },
];

function highlightText(text: string, query: string, term2: string) {
  const terms = [query, term2].filter((t) => t.trim().length > 1);
  if (terms.length === 0) return text;

  let result = text;
  for (const term of terms) {
    const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`(${escaped})`, "gi");
    result = result.replace(regex, '<mark class="search-highlight">$1</mark>');
  }
  return result;
}

function getSnippet(note: Note, query: string): string {
  const plain = note.content_plain || stripHtml(note.content_html);
  if (!query.trim()) return plain.slice(0, 120);
  const idx = plain.toLowerCase().indexOf(query.trim().toLowerCase());
  if (idx === -1) return plain.slice(0, 120);
  const start = Math.max(0, idx - 40);
  return (start > 0 ? "…" : "") + plain.slice(start, start + 140) + (start + 140 < plain.length ? "…" : "");
}

export default function SearchPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [term2, setTerm2] = useState(searchParams.get("t2") || "");
  const [mode, setMode] = useState<SearchMode>((searchParams.get("mode") as SearchMode) || "broad");
  const [categoryId, setCategoryId] = useState(searchParams.get("cat") || "");
  const [categories, setCategories] = useState<Category[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [total, setTotal] = useState(0);
  const [searching, setSearching] = useState(false);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    api.categories.list().then(setCategories).catch(() => {});
  }, []);

  const doSearch = useCallback(async () => {
    if (!query.trim() && !term2.trim()) {
      setNotes([]);
      setTotal(0);
      setSearched(false);
      return;
    }

    setSearching(true);
    setSearched(true);
    try {
      const terms = term2.trim() ? [term2.trim()] : [];
      const result = await api.notes.search({ query: query.trim(), mode, terms });
      let filtered = result.notes;
      if (categoryId) {
        filtered = filtered.filter((n) => n.categories.some((c) => c.id === categoryId));
      }
      setNotes(filtered);
      setTotal(categoryId ? filtered.length : result.total);
    } finally {
      setSearching(false);
    }
  }, [query, term2, mode, categoryId]);

  useEffect(() => {
    const t = setTimeout(doSearch, 350);
    return () => clearTimeout(t);
  }, [doSearch]);

  useEffect(() => {
    const params: Record<string, string> = {};
    if (query) params.q = query;
    if (term2) params.t2 = term2;
    if (mode !== "broad") params.mode = mode;
    if (categoryId) params.cat = categoryId;
    setSearchParams(params, { replace: true });
  }, [query, term2, mode, categoryId, setSearchParams]);

  const activeModeHint = useMemo(
    () => MODES.find((m) => m.id === mode)?.hint || "",
    [mode]
  );

  const openNote = (note: Note) => {
    saveListScroll(note.id);
    navigate(`/notes/${note.id}`);
  };

  return (
    <div className="search-page">
      <div className="search-hero">
        <h1>سرچ کریں</h1>
        <p className="text-muted text-sm m-0">نوٹس میں تلاش — متعدد طریقوں سے</p>

        <div className="search-input-wrap">
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="سرچ کریں..."
            className="search-input"
            autoFocus
          />
          <span className="search-input-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <circle cx="11" cy="11" r="7" />
              <path d="M20 20l-4-4" />
            </svg>
          </span>
        </div>

        <div className="search-modes">
          {MODES.map((m) => (
            <button
              key={m.id}
              type="button"
              className={`search-mode-btn${mode === m.id ? " active" : ""}`}
              onClick={() => setMode(m.id)}
            >
              {m.label}
            </button>
          ))}
        </div>
        {activeModeHint && (
          <p className="text-xs text-muted mt-2 mb-0">{activeModeHint}</p>
        )}

        <div className="search-filters">
          <input
            type="text"
            value={term2}
            onChange={(e) => setTerm2(e.target.value)}
            placeholder="دوسرا لفظ (اختیاری)"
            className="search-select"
          />
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            className="search-select"
          >
            <option value="">کیٹیگری منتخب کیجیے</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
      </div>

      {searching && <p className="text-center text-muted text-sm">تلاش جاری ہے...</p>}

      {!searching && searched && (
        <>
          <p className="search-results-meta">
            {total > 0
              ? `${total} نتائج ملے`
              : "کوئی نتیجہ نہیں ملا"}
          </p>
          <div>
            {notes.map((note) => {
              const snippet = getSnippet(note, query);
              return (
                <button
                  key={note.id}
                  type="button"
                  className="search-result-item w-full text-right"
                  onClick={() => openNote(note)}
                >
                  <p className="search-result-title">{note.display_title}</p>
                  <p
                    className="search-result-snippet m-0"
                    dangerouslySetInnerHTML={{ __html: highlightText(snippet, query, term2) }}
                  />
                  {note.categories.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {note.categories.slice(0, 3).map((c) => (
                        <span key={c.id} className="text-xs bg-badge text-primary px-2 py-0.5 rounded-full">
                          {c.name}
                        </span>
                      ))}
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </>
      )}

      {!searched && !searching && (
        <div className="text-center text-muted py-8">
          <p className="text-base">تلاش کے لیے اوپر لفظ درج کریں</p>
          <p className="text-sm mt-2">آسان سرچ، سنگل پیج سرچ، بالکل موافق یا لفظی سرچ منتخب کریں</p>
        </div>
      )}
    </div>
  );
}
