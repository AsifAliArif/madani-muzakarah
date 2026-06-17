import { useEffect, useRef } from "react";

type WsHandler = (event: string, data: unknown) => void;

export function useWebSocket(onEvent: WsHandler) {
  const handlerRef = useRef(onEvent);
  handlerRef.current = onEvent;

  useEffect(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onmessage = (msg) => {
      try {
        const { event, data } = JSON.parse(msg.data);
        handlerRef.current(event, data);
      } catch { /* ignore */ }
    };

    const interval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 30000);

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, []);
}
