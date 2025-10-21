'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { getStats } from '@/services/storage';
import { SavedOutput } from '@/types';
import { Layers, Play, Database, Plus, ArrowRight, Clock } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalElements: 0,
    totalOutputs: 0,
    recentOutputs: [] as SavedOutput[],
  });

  useEffect(() => {
    setStats(getStats());
  }, []);

  const formatRelativeTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Welcome to Document AI
          </h1>
          <p className="text-gray-600">
            Create dynamic elements, run analyses, and manage your outputs
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Elements</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats.totalElements}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Layers className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Runs</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats.totalOutputs}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Play className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Saved Outputs</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats.totalOutputs}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Database className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Link
            href="/elements?create=true"
            className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white hover:from-blue-600 hover:to-blue-700 transition-all transform hover:scale-105"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">Create Element</h3>
                <p className="text-blue-100 text-sm">
                  Configure a new dynamic element
                </p>
              </div>
              <Plus className="w-8 h-8" />
            </div>
          </Link>

          <Link
            href="/elements"
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-all transform hover:scale-105"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Browse Elements
                </h3>
                <p className="text-gray-600 text-sm">
                  View and manage all elements
                </p>
              </div>
              <Layers className="w-8 h-8 text-gray-400" />
            </div>
          </Link>

          <Link
            href="/outputs"
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-all transform hover:scale-105"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  View Outputs
                </h3>
                <p className="text-gray-600 text-sm">
                  Browse saved analysis results
                </p>
              </div>
              <Database className="w-8 h-8 text-gray-400" />
            </div>
          </Link>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Recent Activity</h2>
            <Link
              href="/outputs"
              className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center"
            >
              View All
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>

          {stats.recentOutputs.length === 0 ? (
            <div className="text-center py-12">
              <Database className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 mb-4">No runs yet</p>
              <Link
                href="/run"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Play className="w-4 h-4 mr-2" />
                Run Your First Element
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {stats.recentOutputs.map((output) => (
                <div
                  key={output.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <h3 className="font-semibold text-gray-900">
                        {output.elementName}
                      </h3>
                    </div>
                    <p className="text-sm text-gray-600 mt-1 line-clamp-1">
                      {output.aiResponse.final_answer}
                    </p>
                    <div className="flex items-center space-x-4 mt-2">
                      <div className="flex items-center text-xs text-gray-500">
                        <Clock className="w-3 h-3 mr-1" />
                        {formatRelativeTime(output.createdAt)}
                      </div>
                      <div className={`text-xs font-medium ${
                        output.aiResponse.metrics.overall_score >= 0.8 ? 'text-green-600' : 'text-yellow-600'
                      }`}>
                        Quality: {Math.round(output.aiResponse.metrics.overall_score * 100)}%
                      </div>
                      <div className="text-xs text-gray-500">
                        {output.aiResponse.processing_time_seconds}s
                      </div>
                      {output.aiResponse.metrics.needs_review && (
                        <span className="text-xs text-red-600 font-medium">⚠ Review</span>
                      )}
                    </div>
                  </div>
                  <Link
                    href={`/outputs?id=${output.id}`}
                    className="ml-4 text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    View
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
