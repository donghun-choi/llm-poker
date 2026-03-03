import React from 'react';

export default function PotDisplay({ pot }) {
  return (
    <div className="rounded-full bg-amber-500/90 text-slate-900 px-4 py-1 text-sm font-semibold shadow-lg">
      Pot: ${pot}
    </div>
  );
}
