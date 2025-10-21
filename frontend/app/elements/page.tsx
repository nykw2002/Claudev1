'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  getElements,
  createElement,
  updateElement,
  deleteElement,
} from '@/services/storage';
import { DynamicElement } from '@/types';
import ElementCard from './components/ElementCard';
import ElementForm from './components/ElementForm';
import { Plus, Layers } from 'lucide-react';

export default function ElementsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [elements, setElements] = useState<DynamicElement[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingElement, setEditingElement] = useState<DynamicElement | undefined>();

  useEffect(() => {
    loadElements();

    // Check if we should auto-open create form
    if (searchParams.get('create') === 'true') {
      setShowForm(true);
    }
  }, [searchParams]);

  const loadElements = () => {
    setElements(getElements());
  };

  const handleCreate = () => {
    setEditingElement(undefined);
    setShowForm(true);
  };

  const handleEdit = (element: DynamicElement) => {
    setEditingElement(element);
    setShowForm(true);
  };

  const handleDelete = (id: string) => {
    if (deleteElement(id)) {
      loadElements();
    }
  };

  const handleRun = (element: DynamicElement) => {
    // Navigate to run page with pre-selected element
    router.push(`/run?elementId=${element.id}`);
  };

  const handleSave = (data: Omit<DynamicElement, 'id' | 'createdAt' | 'updatedAt'>) => {
    if (editingElement) {
      // Update existing element
      updateElement(editingElement.id, data);
    } else {
      // Create new element
      createElement(data);
    }

    setShowForm(false);
    setEditingElement(undefined);
    loadElements();
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingElement(undefined);
  };

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Dynamic Elements
            </h1>
            <p className="text-gray-600">
              Create and manage your document processing configurations
            </p>
          </div>

          <button
            onClick={handleCreate}
            className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all transform hover:scale-105 shadow-md font-medium"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Element
          </button>
        </div>

        {/* Elements Grid */}
        {elements.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
            <Layers className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Elements Yet
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Get started by creating your first dynamic element. Define a prompt,
              configure file types, and add additional context from other elements.
            </p>
            <button
              onClick={handleCreate}
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create First Element
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {elements.map((element) => (
              <ElementCard
                key={element.id}
                element={element}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onRun={handleRun}
              />
            ))}
          </div>
        )}

        {/* Element Count */}
        {elements.length > 0 && (
          <div className="mt-8 text-center text-sm text-gray-500">
            Showing {elements.length} element{elements.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {/* Element Form Modal */}
      {showForm && (
        <ElementForm
          element={editingElement}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      )}
    </div>
  );
}
