export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  role: "admin" | "user";
}

export interface Category {
  id: string;
  name: string;
}

export interface Note {
  id: string;
  title: string | null;
  content_html: string;
  content_plain: string;
  author_name: string;
  status: "active" | "archived" | "trashed";
  categories: Category[];
  created_by: string;
  updated_by: string | null;
  creator_name: string;
  created_at: string;
  updated_at: string;
  display_title: string;
}

const API_BASE = "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (res.status === 401) {
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "خرابی" }));
    throw new Error(err.detail || "خرابی");
  }
  if (res.status === 204) return {} as T;
  return res.json();
}

export const api = {
  me: () => request<User>("/api/auth/me"),
  login: () => { window.location.href = "/api/auth/login"; },
  logout: () => request("/api/auth/logout", { method: "POST" }),
  notes: {
    list: (status = "active") => request<Note[]>(`/api/notes?status=${status}`),
    get: (id: string) => request<Note>(`/api/notes/${id}`),
    create: (data: object) => request<Note>("/api/notes", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: object) => request<Note>(`/api/notes/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    archive: (id: string) => request<Note>(`/api/notes/${id}/archive`, { method: "POST" }),
    trash: (id: string) => request<Note>(`/api/notes/${id}/trash`, { method: "POST" }),
    restore: (id: string) => request<Note>(`/api/notes/${id}/restore`, { method: "POST" }),
    deleteForever: (id: string) => request(`/api/notes/${id}/forever`, { method: "DELETE" }),
    search: (data: object) => request<{ notes: Note[]; total: number }>("/api/notes/search", { method: "POST", body: JSON.stringify(data) }),
  },
  categories: {
    list: () => request<Category[]>("/api/categories"),
  },
  admin: {
    users: () => request<User[]>("/api/admin/users"),
    removeUser: (id: string) => request(`/api/admin/users/${id}/remove`, { method: "POST" }),
    logs: () => request<object[]>("/api/admin/logs"),
    aiSettings: () => request<{ llm_name: string; system_prompt: string; has_api_key: boolean }>("/api/admin/ai-settings"),
    updateAiSettings: (data: object) => request("/api/admin/ai-settings", { method: "PUT", body: JSON.stringify(data) }),
  },
};
