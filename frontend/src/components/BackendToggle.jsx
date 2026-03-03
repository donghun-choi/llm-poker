import React from 'react';

export default function BackendToggle({ value, onChange }) {
  return (
    <div className="flex items-center space-x-3">
      <span className="text-sm text-slate-300">LLM Provider</span>
      <button
        type="button"
        onClick={() => onChange(value === 'openai' ? 'ollama' : 'openai')}
        className={`rounded-full px-4 py-2 text-sm font-semibold shadow border ${
          value === 'openai'
            ? 'bg-emerald-600 border-emerald-400'
            : 'bg-amber-500 text-slate-900 border-amber-300'
        }`}
      >
        {value === 'openai' ? 'OpenAI' : 'Ollama'}
      </button>
    </div>
  );
}
