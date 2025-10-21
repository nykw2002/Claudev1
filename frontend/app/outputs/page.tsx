'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { getOutputs, getElements, deleteOutput } from '@/services/storage';
import { SavedOutput, DynamicElement } from '@/types';
import OutputCard from './components/OutputCard';
import { Database, Filter } from 'lucide-react';

export default function OutputsPage() {
  const searchParams = useSearchParams();
  const [outputs, setOutputs] = useState<SavedOutput[]>([]);
  const [filteredOutputs, setFilteredOutputs] = useState<SavedOutput[]>([]);
  const [elements, setElements] = useState<DynamicElement[]>([]);
  const [filterElementId, setFilterElementId] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest'>('newest');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    applyFiltersAndSort();
  }, [outputs, filterElementId, sortBy]);

  useEffect(() => {
    // Check if we should highlight a specific output
    const outputId = searchParams.get('id');
    if (outputId) {
      // Scroll to element or expand it
      setTimeout(() => {
        const element = document.getElementById(`output-${outputId}`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          element.classList.add('ring-2', 'ring-blue-500');
        }
      }, 100);
    }
  }, [searchParams, filteredOutputs]);

  const loadData = () => {
    const allOutputs = getOutputs();
    const allElements = getElements();
    setOutputs(allOutputs);
    setElements(allElements);
  };

  const applyFiltersAndSort = () => {
    let filtered = [...outputs];

    // Apply element filter
    if (filterElementId !== 'all') {
      filtered = filtered.filter(output => output.elementId === filterElementId);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      const dateA = new Date(a.createdAt).getTime();
      const dateB = new Date(b.createdAt).getTime();
      return sortBy === 'newest' ? dateB - dateA : dateA - dateB;
    });

    setFilteredOutputs(filtered);
  };

  const handleDelete = (id: string) => {
    if (deleteOutput(id)) {
      loadData();
    }
  };

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Saved Outputs
          </h1>
          <p className="text-gray-600">
            Browse and manage your analysis results
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Filters:</span>
            </div>

            {/* Element Filter */}
            <div className="flex-1 max-w-xs">
              <select
                value={filterElementId}
                onChange={(e) => setFilterElementId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm text-gray-900"
              >
                <option value="all">All Elements</option>
                {elements.map(element => (
                  <option key={element.id} value={element.id}>
                    {element.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort */}
            <div className="flex-1 max-w-xs">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'newest' | 'oldest')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm text-gray-900"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
              </select>
            </div>

            {/* Results Count */}
            <div className="text-sm text-gray-600">
              {filteredOutputs.length} result{filteredOutputs.length !== 1 ? 's' : ''}
            </div>
          </div>
        </div>

        {/* Outputs Grid */}
        {filteredOutputs.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
            <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {outputs.length === 0 ? 'No Outputs Yet' : 'No Results Found'}
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              {outputs.length === 0
                ? 'Run an element to generate and save your first output.'
                : 'Try adjusting your filters to find what you\'re looking for.'}
            </p>
            {outputs.length === 0 && (
              <a
                href="/run"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Run an Element
              </a>
            )}
            {outputs.length > 0 && filterElementId !== 'all' && (
              <button
                onClick={() => setFilterElementId('all')}
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredOutputs.map((output) => (
              <div key={output.id} id={`output-${output.id}`}>
                <OutputCard
                  output={output}
                  onDelete={handleDelete}
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
