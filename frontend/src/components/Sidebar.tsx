import { Link, useLocation } from "react-router-dom";
import { User } from "../api/client";

interface Props {
  user: User;
  open: boolean;
  onClose: () => void;
  onLogout: () => void;
}

export default function Sidebar({ user, open, onClose, onLogout }: Props) {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  const linkClass = (path: string) =>
    `sidebar-nav-link${isActive(path) ? " active" : ""}`;

  const handleNav = () => onClose();

  return (
    <>
      {open && <div className="sidebar-overlay" onClick={onClose} aria-hidden="true" />}
      <aside className={`sidebar-drawer${open ? " open" : ""}`} aria-hidden={!open}>
        <button type="button" className="sidebar-close" onClick={onClose} aria-label="بند کریں">
          ✕
        </button>
        <h1 className="font-title text-xl mb-5 text-center leading-snug">مدنی مذاکرہ ڈیٹا بیس</h1>
        <nav>
          <Link to="/" className={linkClass("/")} onClick={handleNav}>تمام نوٹس</Link>
          <Link to="/archive" className={linkClass("/archive")} onClick={handleNav}>آرکائیو</Link>
          <Link to="/search" className={linkClass("/search")} onClick={handleNav}>تلاش</Link>
          {user.role === "admin" && (
            <>
              <Link to="/admin" className={linkClass("/admin")} onClick={handleNav}>ایڈمن پینل</Link>
              <Link to="/admin/trash" className={linkClass("/admin/trash")} onClick={handleNav}>ٹریش</Link>
              <Link to="/admin/logs" className={linkClass("/admin/logs")} onClick={handleNav}>لاگز</Link>
              <Link to="/admin/settings" className={linkClass("/admin/settings")} onClick={handleNav}>AI سیٹنگز</Link>
            </>
          )}
        </nav>
        <div className="mt-6 pt-4 border-t border-white/20">
          <div className="flex items-center gap-3 mb-3">
            {user.avatar_url && (
              <img src={user.avatar_url} alt="" className="w-9 h-9 rounded-full border-2 border-white/30" />
            )}
            <div>
              <p className="text-sm leading-tight">{user.name}</p>
              <p className="text-xs opacity-75">{user.role === "admin" ? "ایڈمن" : "صارف"}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => { onLogout(); onClose(); }}
            className="w-full py-2 text-sm bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
          >
            لاگ آؤٹ
          </button>
        </div>
      </aside>
    </>
  );
}
