import { useEffect, useState } from "react";

interface Log {
  id: string;
  note_id: string | null;
  user_name: string;
  action: string;
  created_at: string;
  previous_state: object | null;
  new_state: object | null;
}

export default function LogsPage() {
  const [logs, setLogs] = useState<Log[]>([]);

  useEffect(() => {
    import("../api/client").then(({ api }) => api.admin.logs().then(setLogs as (l: object[]) => void));
  }, []);

  return (
    <div>
      <h2 className="font-title text-2xl text-primary mb-6">آڈٹ لاگز</h2>
      <div className="space-y-3 max-h-[70vh] overflow-auto">
        {logs.map((log) => (
          <div key={log.id} className="bg-section rounded-card p-4 text-sm">
            <div className="flex justify-between mb-2">
              <span className="font-title text-primary">{log.action}</span>
              <span className="text-gray-500">{new Date(log.created_at).toLocaleString("ur-PK")}</span>
            </div>
            <p>صارف: {log.user_name}</p>
            {log.note_id && <p>نوٹ: {log.note_id}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
