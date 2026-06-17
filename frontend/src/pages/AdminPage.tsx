import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, User } from "../api/client";

export default function AdminPage() {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    api.admin.users().then(setUsers);
  }, []);

  const remove = async (id: string) => {
    if (confirm("کیا آپ اس صارف کو ہٹانا چاہتے ہیں؟")) {
      await api.admin.removeUser(id);
      setUsers((prev) => prev.filter((u) => u.id !== id));
    }
  };

  return (
    <div>
      <h2 className="font-title text-2xl text-primary mb-6">ایڈمن پینل</h2>
      <div className="grid gap-4 md:grid-cols-3 mb-8">
        <Link to="/admin/trash" className="bg-section rounded-card p-6 text-center hover:shadow-md">
          <span className="font-title text-xl text-primary">ٹریش</span>
        </Link>
        <Link to="/admin/logs" className="bg-section rounded-card p-6 text-center hover:shadow-md">
          <span className="font-title text-xl text-primary">لاگز</span>
        </Link>
        <Link to="/admin/settings" className="bg-section rounded-card p-6 text-center hover:shadow-md">
          <span className="font-title text-xl text-primary">AI سیٹنگز</span>
        </Link>
      </div>

      <h3 className="font-title text-xl text-primary mb-4">صارفین</h3>
      <div className="space-y-3">
        {users.map((u) => (
          <div key={u.id} className="flex items-center justify-between bg-section rounded-card p-4">
            <div className="flex items-center gap-3">
              {u.avatar_url && <img src={u.avatar_url} alt="" className="w-10 h-10 rounded-full" />}
              <div>
                <p>{u.name}</p>
                <p className="text-sm text-gray-500">{u.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm bg-badge px-2 py-1 rounded">{u.role === "admin" ? "ایڈمن" : "صارف"}</span>
              {u.role !== "admin" && (
                <button type="button" onClick={() => remove(u.id)} className="text-red-600 text-sm">ہٹائیں</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
