import React from 'react';
import cardImage from '../utils/cardImages.js';

export default function CommunityCards({ cards }) {
  const display = cards || [];
  return (
    <div className="flex space-x-2">
      {display.map((c, idx) => (
        <img
          key={idx}
          src={cardImage(c)}
          alt={`card-${c}`}
          className="h-24 w-16 rounded-md shadow"
        />
      ))}
      {Array.from({ length: 5 - display.length }).map((_, idx) => (
        <div key={`placeholder-${idx}`} className="h-24 w-16 rounded-md border border-emerald-500/30 bg-slate-800/60" />
      ))}
    </div>
  );
}
