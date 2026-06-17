import { useEffect, useState } from "react";

export default function InstallPrompt() {
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferred(e as BeforeInstallPromptEvent);
    };
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  if (!deferred || dismissed) return null;

  return (
    <div className="fixed bottom-20 left-4 right-4 lg:left-auto lg:right-4 lg:w-80 bg-primary text-white rounded-card p-4 shadow-lg z-40">
      <p className="mb-3">ایپ کو ہوم اسکرین پر شامل کریں</p>
      <div className="flex gap-2">
        <button type="button" className="flex-1 py-2 bg-accent rounded-full" onClick={async () => { await deferred.prompt(); setDeferred(null); }}>
          انسٹال
        </button>
        <button type="button" className="px-4 py-2 bg-white/20 rounded-full" onClick={() => setDismissed(true)}>
          بعد میں
        </button>
      </div>
    </div>
  );
}

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: string }>;
}

declare global {
  interface WindowEventMap {
    beforeinstallprompt: BeforeInstallPromptEvent;
  }
}
