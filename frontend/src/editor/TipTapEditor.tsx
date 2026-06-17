import { useEditor, EditorContent, BubbleMenu } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Bold from "@tiptap/extension-bold";
import { Mark, mergeAttributes } from "@tiptap/core";
import { useEffect } from "react";

const Q_START = "\uFD3F";
const Q_END = "\uFD3E";

const QuranText = Mark.create({
  name: "quranText",
  parseHTML() {
    return [{ tag: "span.quran-text" }];
  },
  renderHTML({ HTMLAttributes }) {
    return ["span", mergeAttributes(HTMLAttributes, { class: "quran-text" }), 0];
  },
});

const ArabicText = Mark.create({
  name: "arabicText",
  parseHTML() {
    return [{ tag: "span.arabic-text" }];
  },
  renderHTML({ HTMLAttributes }) {
    return ["span", mergeAttributes(HTMLAttributes, { class: "arabic-text" }), 0];
  },
});

interface Props {
  content: string;
  onChange: (html: string) => void;
}

export default function TipTapEditor({ content, onChange }: Props) {
  const editor = useEditor({
    extensions: [StarterKit.configure({ bold: false }), Bold, QuranText, ArabicText],
    content,
    onUpdate: ({ editor }) => onChange(editor.getHTML()),
    editorProps: {
      attributes: { class: "prose-rtl" },
    },
  });

  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content, false);
    }
  }, [content, editor]);

  const wrapQuran = () => {
    if (!editor) return;
    const { from, to, empty } = editor.state.selection;
    if (empty) return;
    let text = editor.state.doc.textBetween(from, to, "");
    text = text.replace(new RegExp(`[${Q_START}${Q_END}]`, "g"), "").trim();
    const wrapped = `${Q_START}${text}${Q_END}`;
    editor.chain().focus().deleteSelection().insertContent(
      `<span class="quran-text">${wrapped}</span>`
    ).run();
  };

  const wrapArabic = () => {
    if (!editor) return;
    const { from, to, empty } = editor.state.selection;
    if (empty) return;
    const text = editor.state.doc.textBetween(from, to, "");
    editor.chain().focus().deleteSelection().insertContent(
      `<span class="arabic-text">${text}</span>`
    ).run();
  };

  if (!editor) return null;

  return (
    <div className="border border-gray-200 rounded-card overflow-hidden bg-white">
      {editor && (
        <BubbleMenu editor={editor} tippyOptions={{ duration: 100 }}>
          <div className="bubble-menu">
            <button type="button" onClick={() => editor.chain().focus().toggleBold().run()} title="بولڈ">
              B
            </button>
            <button type="button" onClick={wrapQuran} title="قرآنی آیت">
              QR
            </button>
            <button type="button" onClick={wrapArabic} title="عربی">
              AR
            </button>
          </div>
        </BubbleMenu>
      )}
      <EditorContent editor={editor} />
    </div>
  );
}
