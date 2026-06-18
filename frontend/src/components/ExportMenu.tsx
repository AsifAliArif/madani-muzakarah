import { useState } from "react";
import { downloadAsImage, downloadAsPdf, shareAsFile, shareText, buildShareText } from "../export/noteExport";
import ActionButton from "./ActionButton";

interface Props {
  title: string;
  contentHtml: string;
  authorName: string;
}

export default function ExportMenu({ title, contentHtml, authorName }: Props) {
  const [open, setOpen] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);

  return (
    <div className="flex gap-2 flex-wrap">
      <div className="relative">
        <ActionButton variant="primary" onClick={() => { setOpen(!open); setShareOpen(false); }}>
          ڈاؤن لوڈ
        </ActionButton>
        {open && (
          <div className="absolute top-full mt-1 bg-white border rounded-card shadow-elevated z-20 min-w-[140px]">
            <button type="button" className="block w-full text-right px-3 py-2.5 text-sm hover:bg-section" onClick={() => { downloadAsImage(title, contentHtml, authorName); setOpen(false); }}>
              تصویر
            </button>
            <button type="button" className="block w-full text-right px-3 py-2.5 text-sm hover:bg-section" onClick={() => { downloadAsPdf(title, contentHtml, authorName); setOpen(false); }}>
              PDF
            </button>
          </div>
        )}
      </div>

      <div className="relative">
        <ActionButton variant="accent" onClick={() => { setShareOpen(!shareOpen); setOpen(false); }}>
          شیئر
        </ActionButton>
        {shareOpen && (
          <div className="absolute top-full mt-1 bg-white border rounded-card shadow-elevated z-20 min-w-[150px]">
            <button type="button" className="block w-full text-right px-3 py-2.5 text-sm hover:bg-section" onClick={() => { shareAsFile("image", title, contentHtml, authorName); setShareOpen(false); }}>
              تصویر
            </button>
            <button type="button" className="block w-full text-right px-3 py-2.5 text-sm hover:bg-section" onClick={() => { shareAsFile("pdf", title, contentHtml, authorName); setShareOpen(false); }}>
              PDF
            </button>
            <button type="button" className="block w-full text-right px-3 py-2.5 text-sm hover:bg-section" onClick={() => {
              shareText(buildShareText(title, contentHtml, authorName), title);
              setShareOpen(false);
            }}>
              ٹیکسٹ
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
