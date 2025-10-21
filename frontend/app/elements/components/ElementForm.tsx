'use client';

import React, { useState, useEffect } from 'react';
import { DynamicElement, AdditionalContext } from '@/types';
import { getElements } from '@/services/storage';
import { X, FileText, Link2, Plus, Trash2 } from 'lucide-react';

interface ElementFormProps {
  element?: DynamicElement;
  onSave: (data: Omit<DynamicElement, 'id' | 'createdAt' | 'updatedAt'>) => void;
  onCancel: () => void;
}

export default function ElementForm({ element, onSave, onCancel }: ElementFormProps) {
  const [formData, setFormData] = useState({
    name: element?.name || '',
    description: element?.description || '',
    fileType: element?.fileType || 'pdf' as const,
    prompt: element?.prompt || '',
    additionalContext: element?.additionalContext || [] as AdditionalContext[],
  });

  const [availableElements, setAvailableElements] = useState<DynamicElement[]>([]);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    const elements = getElements();
    // Filter out the current element (when editing)
    setAvailableElements(elements.filter(el => el.id !== element?.id));
  }, [element]);

  const validate = () => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.prompt.trim()) {
      newErrors.prompt = 'Prompt is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    onSave(formData);
  };

  const handleAddContext = () => {
    setFormData({
      ...formData,
      additionalContext: [
        ...formData.additionalContext,
        { elementId: '', useLatestOutput: true }
      ]
    });
  };

  const handleRemoveContext = (index: number) => {
    setFormData({
      ...formData,
      additionalContext: formData.additionalContext.filter((_, i) => i !== index)
    });
  };

  const handleContextChange = (index: number, field: keyof AdditionalContext, value: any) => {
    const newContext = [...formData.additionalContext];
    newContext[index] = { ...newContext[index], [field]: value };
    setFormData({ ...formData, additionalContext: newContext });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">
            {element ? 'Edit Element' : 'Create New Element'}
          </h2>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Element Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-gray-900 ${
                errors.name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., Israel Complaints Analysis"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none text-gray-900"
              placeholder="Describe what this element analyzes..."
            />
          </div>

          {/* File Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              File Type
            </label>
            <div className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-gray-400" />
              <select
                value={formData.fileType}
                onChange={(e) => setFormData({ ...formData, fileType: e.target.value as 'pdf' })}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-gray-900"
              >
                <option value="pdf">PDF</option>
              </select>
            </div>
          </div>

          {/* Prompt */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prompt *
            </label>
            <textarea
              value={formData.prompt}
              onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
              rows={5}
              maxLength={500}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none text-gray-900 ${
                errors.prompt ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., How many complaints are from Israel?"
            />
            <div className="flex justify-between mt-1">
              {errors.prompt && (
                <p className="text-sm text-red-600">{errors.prompt}</p>
              )}
              <p className="text-xs text-gray-500 ml-auto">
                {formData.prompt.length}/500
              </p>
            </div>
          </div>

          {/* Additional Context */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700">
                Additional Context
              </label>
              <button
                type="button"
                onClick={handleAddContext}
                className="flex items-center text-sm text-blue-600 hover:text-blue-700 font-medium"
                disabled={availableElements.length === 0}
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Context
              </button>
            </div>

            {formData.additionalContext.length === 0 ? (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                <Link2 className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">
                  No additional context added
                </p>
                {availableElements.length === 0 && (
                  <p className="text-xs text-gray-400 mt-1">
                    Create other elements first to use them as context
                  </p>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {formData.additionalContext.map((context, index) => (
                  <div
                    key={index}
                    className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <select
                      value={context.elementId}
                      onChange={(e) => handleContextChange(index, 'elementId', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm text-gray-900"
                    >
                      <option value="">Select an element...</option>
                      {availableElements.map(el => (
                        <option key={el.id} value={el.id}>
                          {el.name}
                        </option>
                      ))}
                    </select>

                    <label className="flex items-center text-sm text-gray-700 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={context.useLatestOutput}
                        onChange={(e) => handleContextChange(index, 'useLatestOutput', e.target.checked)}
                        className="mr-2 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      Latest
                    </label>

                    <button
                      type="button"
                      onClick={() => handleRemoveContext(index)}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              {element ? 'Save Changes' : 'Create Element'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
