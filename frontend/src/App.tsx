import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import Sidebar from "./components/Sidebar";
import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage";
import NoteDetailPage from "./pages/NoteDetailPage";
import ArchivePage from "./pages/ArchivePage";
import AdminPage from "./pages/AdminPage";
import TrashPage from "./pages/TrashPage";
import LogsPage from "./pages/LogsPage";
import SettingsPage from "./pages/SettingsPage";
import InstallPrompt from "./components/InstallPrompt";
import { api } from "./api/client";

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">لوڈ ہو رہا ہے...</div>;
  }
  if (!user) return <Navigate to="/login" replace />;

  const logout = async () => {
    await api.logout();
    navigate("/login");
  };

  return (
    <div className="app-layout">
      <Sidebar user={user} onLogout={logout} />
      <main className="p-4 lg:p-8 max-w-[1320px]">
        {children}
        <InstallPrompt />
      </main>
    </div>
  );
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAdmin, loading } = useAuth();
  if (loading) return null;
  if (!isAdmin) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<ProtectedLayout><HomePage /></ProtectedLayout>} />
      <Route path="/archive" element={<ProtectedLayout><ArchivePage /></ProtectedLayout>} />
      <Route path="/notes/:id" element={<ProtectedLayout><NoteDetailPage /></ProtectedLayout>} />
      <Route path="/admin" element={<ProtectedLayout><AdminRoute><AdminPage /></AdminRoute></ProtectedLayout>} />
      <Route path="/admin/trash" element={<ProtectedLayout><AdminRoute><TrashPage /></AdminRoute></ProtectedLayout>} />
      <Route path="/admin/logs" element={<ProtectedLayout><AdminRoute><LogsPage /></AdminRoute></ProtectedLayout>} />
      <Route path="/admin/settings" element={<ProtectedLayout><AdminRoute><SettingsPage /></AdminRoute></ProtectedLayout>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
