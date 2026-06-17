import { useEffect, useState } from "react";
import { api, Category } from "../api/client";

interface Props {
  selected: string[];
  onChange: (names: string[]) => void;
}

export default function CategoryPicker({ selected, onChange }: Props) {
  const [all, setAll] = useState<Category[]>([]);
  const [input, setInput] = useState("");
  const [showList, setShowList] = useState(false);

  useEffect(() => {
    api.categories.list().then(setAll).catch(() => {});
  }, []);

  const filtered = all.filter(
    (c) => c.name.includes(input) && !selected.includes(c.name)
  );

  const add = (name: string) => {
    const n = name.trim();
    if (n && !selected.includes(n)) onChange([...selected, n]);
    setInput("");
    setShowList(false);
  };

  const remove = (name: string) => onChange(selected.filter((s) => s !== name));

  return (
    <div className="relative">
      <label className="block text-primary font-title mb-2">کیٹگریز</label>
      <div className="flex flex-wrap gap-2 mb-2">
        {selected.map((name) => (
          <span key={name} className="bg-badge text-primary px-3 py-1 rounded-full flex items-center gap-2">
            {name}
            <button type="button" onClick={() => remove(name)} className="text-red-600">×</button>
          </span>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => { setInput(e.target.value); setShowList(true); }}
        onFocus={() => setShowList(true)}
        onKeyDown={(e) => {
          if (e.key === "Enter") { e.preventDefault(); add(input); }
        }}
        placeholder="کیٹگری تلاش یا نئی بنائیں..."
        className="w-full border border-gray-300 rounded-lg px-4 py-2 text-base"
      />
      {showList && (filtered.length > 0 || input.trim()) && (
        <ul className="absolute z-10 w-full bg-white border rounded-lg shadow-lg mt-1 max-h-40 overflow-auto">
          {filtered.map((c) => (
            <li key={c.id}>
              <button type="button" className="w-full text-right px-4 py-2 hover:bg-section" onClick={() => add(c.name)}>
                {c.name}
              </button>
            </li>
          ))}
          {input.trim() && !all.some((c) => c.name === input.trim()) && (
            <li>
              <button type="button" className="w-full text-right px-4 py-2 hover:bg-section text-accent" onClick={() => add(input)}>
                + نئی کیٹگری: {input}
              </button>
            </li>
          )}
        </ul>
      )}
    </div>
  );
}
