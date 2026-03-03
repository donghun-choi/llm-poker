import React from 'react';

const personalityColors = {
  rock: 'bg-slate-700 border-slate-500',
  shark: 'bg-blue-700 border-blue-400',
  maniac: 'bg-red-700 border-red-400',
  fish: 'bg-emerald-700 border-emerald-400',
};

export default function ReasoningBubble({ text, personality }) {
  const colorClass = personalityColors[personality] || 'bg-slate-700 border-slate-500';
  return (
    <div className={`mt-2 rounded-xl border px-3 py-2 text-xs text-slate-100 shadow-lg ${colorClass}`}>
      {text}
    </div>
  );
}
