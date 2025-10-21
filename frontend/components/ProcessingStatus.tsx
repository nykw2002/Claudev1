'use client';

import React from 'react';
import { Loader2, CheckCircle, XCircle, Upload, Brain } from 'lucide-react';
import { ProcessingStatus as Status } from '@/types';

interface ProcessingStatusProps {
  status: Status;
  message?: string;
}

export default function ProcessingStatus({ status, message }: ProcessingStatusProps) {
  if (status === 'idle') return null;

  const getStatusConfig = () => {
    switch (status) {
      case 'uploading':
        return {
          icon: <Upload className="w-6 h-6 animate-pulse" />,
          text: 'Uploading files...',
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
        };
      case 'processing':
        return {
          icon: <Brain className="w-6 h-6 animate-pulse" />,
          text: 'AI is processing your documents...',
          color: 'text-primary-600',
          bgColor: 'bg-primary-50',
          borderColor: 'border-primary-200',
        };
      case 'complete':
        return {
          icon: <CheckCircle className="w-6 h-6" />,
          text: 'Processing complete!',
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
        };
      case 'error':
        return {
          icon: <XCircle className="w-6 h-6" />,
          text: 'An error occurred',
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
        };
      default:
        return {
          icon: <Loader2 className="w-6 h-6 animate-spin" />,
          text: 'Processing...',
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={`
      p-4 rounded-lg border ${config.bgColor} ${config.borderColor}
      transition-all duration-300 animate-in fade-in slide-in-from-top-2
    `}>
      <div className="flex items-center space-x-3">
        <div className={config.color}>
          {config.icon}
        </div>
        <div className="flex-1">
          <p className={`font-medium ${config.color}`}>
            {config.text}
          </p>
          {message && (
            <p className="text-sm text-gray-600 mt-1">
              {message}
            </p>
          )}
        </div>
        {(status === 'uploading' || status === 'processing') && (
          <Loader2 className={`w-5 h-5 animate-spin ${config.color}`} />
        )}
      </div>

      {status === 'processing' && (
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-primary-500 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            This may take a few moments depending on document size...
          </p>
        </div>
      )}
    </div>
  );
}
