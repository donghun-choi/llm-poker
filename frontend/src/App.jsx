import React, { useEffect, useMemo, useState } from 'react';
import Table from './components/Table.jsx';
import BackendToggle from './components/BackendToggle.jsx';
import useGameSocket from './hooks/useGameSocket.js';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const initialPlayers = [
  { id: 'you', name: 'You', stack: 2000, isHuman: true, personality: null, icon: '🧑' },
  { id: 'p1', name: '🪨 The Rock', stack: 2000, isHuman: false, personality: 'rock', icon: '🪨' },
  { id: 'p2', name: '🦈 The Shark', stack: 2000, isHuman: false, personality: 'shark', icon: '🦈' },
  { id: 'p3', name: '🔥 The Maniac', stack: 2000, isHuman: false, personality: 'maniac', icon: '🔥' },
  { id: 'p4', name: '🐟 The Fish', stack: 2000, isHuman: false, personality: 'fish', icon: '🐟' },
  { id: 'p5', name: '🦈 The Shark 2', stack: 2000, isHuman: false, personality: 'shark', icon: '🦈' },
];

function App() {
  const [gameId, setGameId] = useState(null);
  const [players, setPlayers] = useState(initialPlayers);
  const [communityCards, setCommunityCards] = useState([]);
  const [pot, setPot] = useState(0);
  const [reasoning, setReasoning] = useState({});
  const [provider, setProvider] = useState('openai');

  const { events } = useGameSocket(gameId);

  useEffect(() => {
    async function createGame() {
      try {
        const res = await fetch(`${API_BASE}/api/game/new`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        });
        const json = await res.json();
        setGameId(json.game_id);
      } catch (err) {
        console.error('Failed to create game', err);
      }
    }
    createGame();
  }, []);

  useEffect(() => {
    if (!events.length) return;
    const latest = events[events.length - 1];
    if (latest.type === 'showdown') {
      setCommunityCards(latest.data.community_cards || []);
    }
    if (latest.type === 'hand_result') {
      setPot(0);
    }
  }, [events]);

  const onAction = (action) => {
    console.log('Human action', action);
  };

  const onToggleProvider = async (value) => {
    setProvider(value);
    if (!gameId) return;
    await fetch(`${API_BASE}/api/game/${gameId}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ llm_provider: value }),
    });
  };

  const activePlayer = useMemo(() => players[0], [players]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="mx-auto max-w-6xl px-4 py-6 space-y-4">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">LLM Poker Bot</h1>
            <p className="text-sm text-slate-400">Play 6-max Texas Hold'em against AI personalities.</p>
          </div>
          <BackendToggle value={provider} onChange={onToggleProvider} />
        </header>

        <Table
          players={players}
          communityCards={communityCards}
          pot={pot}
          activePlayerId={activePlayer.id}
          reasoning={reasoning}
          onAction={onAction}
        />
      </div>
    </div>
  );
}

export default App;
