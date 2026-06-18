const SCROLL_Y_KEY = "notesScrollY";
const SCROLL_ID_KEY = "notesScrollId";

export function saveListScroll(noteId: string) {
  sessionStorage.setItem(SCROLL_Y_KEY, String(window.scrollY));
  sessionStorage.setItem(SCROLL_ID_KEY, noteId);
}

export function restoreListScroll() {
  const noteId = sessionStorage.getItem(SCROLL_ID_KEY);
  const scrollY = sessionStorage.getItem(SCROLL_Y_KEY);
  if (!noteId && !scrollY) return;

  sessionStorage.removeItem(SCROLL_ID_KEY);
  sessionStorage.removeItem(SCROLL_Y_KEY);

  requestAnimationFrame(() => {
    setTimeout(() => {
      const el = noteId ? document.getElementById(`note-${noteId}`) : null;
      if (el) {
        el.scrollIntoView({ block: "center", behavior: "auto" });
      } else if (scrollY) {
        window.scrollTo({ top: parseInt(scrollY, 10), behavior: "auto" });
      }
    }, 50);
  });
}
