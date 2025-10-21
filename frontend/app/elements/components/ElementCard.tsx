'use client';

import React from 'react';
import Link from 'next/link';
import { DynamicElement } from '@/types';
import { FileText, Play, Edit, Trash2, Link2 } from 'lucide-react';

interface ElementCardProps {
  element: DynamicElement;
  onEdit: (element: DynamicElement) => void;
  onDelete: (id: string) => void;
  onRun: (element: DynamicElement) => void;
}

export default function ElementCard({ element, onEdit, onDelete, onRun }: ElementCardProps) {
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Are you sure you want to delete "${element.name}"?`)) {
      onDelete(element.id);
    }
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit(element);
  };

  const handleRun = (e: React.MouseEvent) => {
    e.stopPropagation();
    onRun(element);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200 overflow-hidden">
      {/* Card Header */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
            {element.name}
          </h3>
          <div className="flex items-center space-x-1 ml-2">
            <button
              onClick={handleEdit}
              className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="Edit"
            >
              <Edit className="w-4 h-4" />
            </button>
            <button
              onClick={handleDelete}
              className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Description */}
        {element.description && (
          <p className="text-sm text-gray-600 line-clamp-2 mb-4">
            {element.description}
          </p>
        )}

        {/* File Type Badge */}
        <div className="flex items-center space-x-2 mb-4">
          <div className="inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded-full">
            <FileText className="w-3 h-3 mr-1" />
            {element.fileType.toUpperCase()}
          </div>

          {element.additionalContext.length > 0 && (
            <div className="inline-flex items-center px-3 py-1 bg-purple-50 text-purple-700 text-xs font-medium rounded-full">
              <Link2 className="w-3 h-3 mr-1" />
              {element.additionalContext.length} Context{element.additionalContext.length > 1 ? 's' : ''}
            </div>
          )}
        </div>

        {/* Prompt Preview */}
        <div className="bg-gray-50 rounded-lg p-3 mb-4">
          <p className="text-xs font-medium text-gray-500 mb-1">Prompt:</p>
          <p className="text-sm text-gray-700 line-clamp-2">
            {element.prompt}
          </p>
        </div>

        {/* Metadata */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Updated {formatDate(element.updatedAt)}</span>
        </div>
      </div>

      {/* Card Footer - Actions */}
      <div className="bg-gray-50 px-6 py-3 border-t border-gray-200">
        <button
          onClick={handleRun}
          className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
        >
          <Play className="w-4 h-4 mr-2" />
          Run Element
        </button>
      </div>
    </div>
  );
}
