import { useEffect, useState } from 'react';

export default function useGameSocket(gameId) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    if (!gameId) return undefined;
    const ws = new WebSocket(`ws://localhost:8000/ws/game/${gameId}`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setEvents((prev) => [...prev, data]);
        if (data.type === 'your_turn') {
          ws.send(JSON.stringify({ action: 'check' }));
        }
      } catch (err) {
        console.error('WS parse error', err);
      }
    };
    return () => ws.close();
  }, [gameId]);

  return { events };
}
