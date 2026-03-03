import { useEffect, useRef, useState } from 'react';

export default function useGameSocket(gameId) {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!gameId) return undefined;
    const ws = new WebSocket(`ws://localhost:8000/ws/game/${gameId}`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setEvents((prev) => [...prev, data]);
      } catch (err) {
        console.error('WS parse error', err);
      }
    };

    return () => {
      setConnected(false);
      ws.close();
    };
  }, [gameId]);

  const sendAction = (action) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(action));
    }
  };

  return { events, sendAction, connected };
}
