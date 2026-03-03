import React from 'react';
import PlayerSeat from './PlayerSeat.jsx';
import CommunityCards from './CommunityCards.jsx';
import PotDisplay from './PotDisplay.jsx';
import ActionPanel from './ActionPanel.jsx';

const seatAngles = [270, 330, 30, 90, 150, 210];

function seatStyle(idx) {
  const angle = seatAngles[idx];
  const radius = 230;
  const x = 50 + radius * Math.cos((angle * Math.PI) / 180);
  const y = 50 + radius * Math.sin((angle * Math.PI) / 180);
  return {
    left: `${x}%`,
    top: `${y}%`,
    transform: 'translate(-50%, -50%)',
  };
}

export default function Table({ players, communityCards, pot, activePlayerId, reasoning, onAction }) {
  return (
    <div className="relative h-[600px] w-full rounded-3xl table-bg shadow-2xl border border-emerald-500/30 overflow-hidden">
      <div className="absolute inset-0">
        {players.map((p, idx) => (
          <div key={p.id} className="absolute" style={seatStyle(idx)}>
            <PlayerSeat player={p} active={p.id === activePlayerId} reasoning={reasoning[p.id]} />
          </div>
        ))}
      </div>
      <div className="absolute inset-0 flex flex-col items-center justify-center space-y-4 pointer-events-none">
        <CommunityCards cards={communityCards} />
        <PotDisplay pot={pot} />
      </div>
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 w-[70%]">
        <ActionPanel onAction={onAction} />
      </div>
    </div>
  );
}
