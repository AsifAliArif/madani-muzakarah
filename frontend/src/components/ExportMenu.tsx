import { useState } from "react";
import { downloadAsImage, downloadAsPdf, shareAsFile, shareText, buildShareText } from "../export/noteExport";

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
        <button
          type="button"
          className="px-4 py-2 bg-primary text-white rounded-full text-base min-h-[44px]"
          onClick={() => { setOpen(!open); setShareOpen(false); }}
        >
          ڈاؤن لوڈ
        </button>
        {open && (
          <div className="absolute top-full mt-1 bg-white border rounded-card shadow-lg z-20 min-w-[160px]">
            <button type="button" className="block w-full text-right px-4 py-3 hover:bg-section" onClick={() => { downloadAsImage(title, contentHtml, authorName); setOpen(false); }}>
              تصویر (PNG)
            </button>
            <button type="button" className="block w-full text-right px-4 py-3 hover:bg-section" onClick={() => { downloadAsPdf(title, contentHtml, authorName); setOpen(false); }}>
              PDF
            </button>
          </div>
        )}
      </div>

      <div className="relative">
        <button
          type="button"
          className="px-4 py-2 bg-accent text-white rounded-full text-base min-h-[44px]"
          onClick={() => { setShareOpen(!shareOpen); setOpen(false); }}
        >
          شیئر
        </button>
        {shareOpen && (
          <div className="absolute top-full mt-1 bg-white border rounded-card shadow-lg z-20 min-w-[180px]">
            <button type="button" className="block w-full text-right px-4 py-3 hover:bg-section" onClick={() => { shareAsFile("image", title, contentHtml, authorName); setShareOpen(false); }}>
              تصویر شیئر
            </button>
            <button type="button" className="block w-full text-right px-4 py-3 hover:bg-section" onClick={() => { shareAsFile("pdf", title, contentHtml, authorName); setShareOpen(false); }}>
              PDF شیئر
            </button>
            <button type="button" className="block w-full text-right px-4 py-3 hover:bg-section" onClick={() => {
              shareText(buildShareText(title, contentHtml, authorName), title);
              setShareOpen(false);
            }}>
              ٹیکسٹ شیئر
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
