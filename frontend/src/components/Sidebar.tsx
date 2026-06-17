import { Link, useLocation } from "react-router-dom";
import { User } from "../api/client";

interface Props {
  user: User;
  onLogout: () => void;
}

export default function Sidebar({ user, onLogout }: Props) {
  const location = useLocation();
  const linkClass = (path: string) =>
    `block px-4 py-3 rounded-lg mb-1 ${location.pathname === path ? "bg-accent text-white" : "text-white hover:bg-primary-light"}`;

  return (
    <aside className="bg-primary text-white p-4 lg:min-h-screen">
      <h1 className="font-title text-2xl mb-6 text-center">مدنی مذاکرہ ڈیٹا بیس</h1>
      <nav className="space-y-1">
        <Link to="/" className={linkClass("/")}>تمام نوٹس</Link>
        <Link to="/archive" className={linkClass("/archive")}>آرکائیو</Link>
        {user.role === "admin" && (
          <>
            <Link to="/admin" className={linkClass("/admin")}>ایڈمن پینل</Link>
            <Link to="/admin/trash" className={linkClass("/admin/trash")}>ٹریش</Link>
            <Link to="/admin/logs" className={linkClass("/admin/logs")}>لاگز</Link>
            <Link to="/admin/settings" className={linkClass("/admin/settings")}>AI سیٹنگز</Link>
          </>
        )}
      </nav>
      <div className="mt-8 pt-4 border-t border-white/20">
        <div className="flex items-center gap-3 mb-3">
          {user.avatar_url && <img src={user.avatar_url} alt="" className="w-10 h-10 rounded-full" />}
          <div>
            <p className="text-sm">{user.name}</p>
            <p className="text-xs opacity-75">{user.role === "admin" ? "ایڈمن" : "صارف"}</p>
          </div>
        </div>
        <button type="button" onClick={onLogout} className="w-full py-2 bg-white/10 rounded-lg hover:bg-white/20">
          لاگ آؤٹ
        </button>
      </div>
    </aside>
  );
}
