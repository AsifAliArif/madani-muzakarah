import { useNavigate } from "react-router-dom";

interface Props {
  onMenuOpen: () => void;
  title?: string;
}

function SearchIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-4-4" />
    </svg>
  );
}

function MenuIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <path d="M4 7h16M4 12h16M4 17h16" />
    </svg>
  );
}

export default function AppHeader({ onMenuOpen, title = "مدنی مذاکرہ ڈیٹا بیس" }: Props) {
  const navigate = useNavigate();

  return (
    <header className="app-header">
      <button type="button" className="header-icon-btn" onClick={onMenuOpen} aria-label="مینو">
        <MenuIcon />
      </button>
      <span className="app-header-title">{title}</span>
      <button
        type="button"
        className="search-circle-btn"
        onClick={() => navigate("/search")}
        aria-label="تلاش"
      >
        <SearchIcon />
      </button>
    </header>
  );
}
