import React, { useState } from 'react';

export default function ActionPanel({ onAction, disabled }) {
  const [raiseSize, setRaiseSize] = useState(50);

  return (
    <div className="rounded-2xl bg-slate-800/80 border border-slate-700 px-4 py-3 shadow-lg backdrop-blur">
      <div className="flex items-center space-x-3">
        <button
          type="button"
          className="rounded-lg bg-slate-700 px-3 py-2 text-sm font-semibold hover:bg-slate-600 disabled:opacity-40"
          disabled={disabled}
          onClick={() => onAction({ action: 'fold' })}
        >
          Fold
        </button>
        <button
          type="button"
          className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-semibold hover:bg-emerald-500 disabled:opacity-40"
          disabled={disabled}
          onClick={() => onAction({ action: 'call' })}
        >
          Call
        </button>
        <button
          type="button"
          className="rounded-lg bg-amber-500 px-3 py-2 text-sm font-semibold text-slate-900 hover:bg-amber-400 disabled:opacity-40"
          disabled={disabled}
          onClick={() => onAction({ action: 'raise', amount: raiseSize })}
        >
          Raise ${raiseSize}
        </button>
        <input
          type="range"
          min="10"
          max="500"
          value={raiseSize}
          onChange={(e) => setRaiseSize(Number(e.target.value))}
          className="w-40"
        />
      </div>
    </div>
  );
}
