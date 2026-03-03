import React from 'react';
import ReasoningBubble from './ReasoningBubble.jsx';

export default function PlayerSeat({ player, active, reasoning }) {
  return (
    <div className={`relative w-44 rounded-2xl border border-emerald-400/30 bg-slate-900/70 p-3 shadow-lg ${active ? 'ring-2 ring-amber-400' : ''}`}>
      <div className="flex items-center space-x-2">
        <span className="text-xl">{player.icon}</span>
        <div>
          <div className="text-sm font-semibold text-white">{player.name}</div>
          <div className="text-xs text-emerald-300">${player.stack}</div>
        </div>
      </div>
      <div className="mt-2 flex space-x-2">
        <div className="h-16 w-10 rounded-md border border-slate-600 bg-slate-800 flex items-center justify-center text-slate-400 text-xs">?
        </div>
        <div className="h-16 w-10 rounded-md border border-slate-600 bg-slate-800 flex items-center justify-center text-slate-400 text-xs">?
        </div>
      </div>
      {reasoning && <ReasoningBubble text={reasoning} personality={player.personality} />}
    </div>
  );
}
