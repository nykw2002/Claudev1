'use client';

import React, { useState } from 'react';
import { MessageSquare } from 'lucide-react';

interface PromptInputProps {
  onPromptChange: (prompt: string) => void;
  disabled?: boolean;
  value?: string;
}

export default function PromptInput({ onPromptChange, disabled = false, value = '' }: PromptInputProps) {
  const [prompt, setPrompt] = useState(value);
  const maxLength = 1000;

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (newValue.length <= maxLength) {
      setPrompt(newValue);
      onPromptChange(newValue);
    }
  };

  return (
    <div className="w-full">
      <label htmlFor="prompt" className="flex items-center text-sm font-medium text-gray-700 mb-2">
        <MessageSquare className="w-4 h-4 mr-2" />
        Your Question
      </label>
      <textarea
        id="prompt"
        value={prompt}
        onChange={handleChange}
        disabled={disabled}
        placeholder="Enter your question about the documents... (e.g., How many complaints are from Israel?)"
        className={`
          w-full px-4 py-3 rounded-lg border border-gray-300
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
          resize-none transition-all text-gray-900
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
        `}
        rows={4}
      />
      <div className="flex justify-between items-center mt-2">
        <p className="text-xs text-gray-500">
          Ask any question about the uploaded documents
        </p>
        <p className={`text-xs ${prompt.length > maxLength * 0.9 ? 'text-orange-500' : 'text-gray-400'}`}>
          {prompt.length} / {maxLength}
        </p>
      </div>
    </div>
  );
}
