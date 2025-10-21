'use client';

import React, { useState } from 'react';
import { SavedOutput } from '@/types';
import { Clock, FileText, Trash2, ChevronDown, ChevronUp, Award, Target, CheckCircle, AlertTriangle, TrendingUp, Shield } from 'lucide-react';

interface OutputCardProps {
  output: SavedOutput;
  onDelete: (id: string) => void;
}

export default function OutputCard({ output, onDelete }: OutputCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

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

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this output?')) {
      onDelete(output.id);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-700 bg-green-100';
    if (score >= 0.6) return 'text-yellow-700 bg-yellow-100';
    return 'text-red-700 bg-red-100';
  };

  const getScoreColorBorder = (score: number) => {
    if (score >= 0.8) return 'border-green-200 bg-green-50';
    if (score >= 0.6) return 'border-yellow-200 bg-yellow-50';
    return 'border-red-200 bg-red-50';
  };

  return (
    <div className={`bg-white rounded-xl shadow-sm border-2 overflow-hidden ${
      output.aiResponse.metrics.needs_review ? 'border-red-300' : 'border-gray-200'
    }`}>
      {/* Warning Banner for Low Quality */}
      {output.aiResponse.metrics.needs_review && (
        <div className="bg-red-50 border-b-2 border-red-200 px-6 py-3">
          <div className="flex items-center space-x-2 text-red-800">
            <AlertTriangle className="w-5 h-5" />
            <span className="font-semibold text-sm">
              Needs Review: Overall quality score below 80%
            </span>
          </div>
        </div>
      )}

      {/* Card Header */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {output.elementName}
            </h3>
            <div className="flex items-center text-sm text-gray-500 space-x-4">
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                {formatRelativeTime(output.createdAt)}
              </div>
              <div className="flex items-center">
                <FileText className="w-4 h-4 mr-1" />
                {output.files.length} file{output.files.length > 1 ? 's' : ''}
              </div>
            </div>
          </div>
          <button
            onClick={handleDelete}
            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Delete output"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>

        {/* Final Answer Preview */}
        <div className="mb-4">
          <p className={`text-gray-700 ${isExpanded ? '' : 'line-clamp-3'}`}>
            {output.aiResponse.final_answer}
          </p>
        </div>

        {/* Overall Score - Prominent Display */}
        <div className={`mb-4 p-4 rounded-lg border-2 ${getScoreColorBorder(output.aiResponse.metrics.overall_score)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Award className={`w-6 h-6 ${output.aiResponse.metrics.overall_score >= 0.8 ? 'text-green-600' : 'text-yellow-600'}`} />
              <div>
                <p className="text-sm font-medium text-gray-700">Overall Quality Score</p>
                <p className="text-xs text-gray-500">Average of Groundedness, Accuracy, Relevance</p>
              </div>
            </div>
            <div className="text-right">
              <p className={`text-3xl font-bold ${output.aiResponse.metrics.overall_score >= 0.8 ? 'text-green-700' : 'text-yellow-700'}`}>
                {Math.round(output.aiResponse.metrics.overall_score * 100)}%
              </p>
              <p className="text-xs text-gray-500">
                {output.aiResponse.processing_time_seconds}s processing
              </p>
            </div>
          </div>
        </div>

        {/* New Evaluation Metrics Grid */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {/* Groundedness */}
          <div className={`text-center p-3 rounded-lg border ${getScoreColorBorder(output.aiResponse.metrics.groundedness)}`}>
            <div className="flex items-center justify-center mb-1">
              <Shield className="w-4 h-4 text-blue-600" />
            </div>
            <p className="text-xl font-bold text-gray-900">
              {Math.round(output.aiResponse.metrics.groundedness * 100)}%
            </p>
            <p className="text-xs text-gray-600">Groundedness</p>
            {output.aiResponse.metrics.groundedness_justification && (
              <details className="mt-2">
                <summary className="text-xs text-blue-700 cursor-pointer hover:text-blue-900">
                  Why?
                </summary>
                <p className="mt-1 text-xs text-gray-700 text-left bg-white p-2 rounded border border-blue-200">
                  {output.aiResponse.metrics.groundedness_justification.substring(0, 100)}...
                </p>
              </details>
            )}
          </div>

          {/* Accuracy */}
          <div className={`text-center p-3 rounded-lg border ${getScoreColorBorder(output.aiResponse.metrics.accuracy)}`}>
            <div className="flex items-center justify-center mb-1">
              <Target className="w-4 h-4 text-green-600" />
            </div>
            <p className="text-xl font-bold text-gray-900">
              {Math.round(output.aiResponse.metrics.accuracy * 100)}%
            </p>
            <p className="text-xs text-gray-600">Accuracy</p>
            {output.aiResponse.metrics.accuracy_justification && (
              <details className="mt-2">
                <summary className="text-xs text-green-700 cursor-pointer hover:text-green-900">
                  Why?
                </summary>
                <p className="mt-1 text-xs text-gray-700 text-left bg-white p-2 rounded border border-green-200">
                  {output.aiResponse.metrics.accuracy_justification.substring(0, 100)}...
                </p>
              </details>
            )}
          </div>

          {/* Relevance */}
          <div className={`text-center p-3 rounded-lg border ${getScoreColorBorder(output.aiResponse.metrics.relevance)}`}>
            <div className="flex items-center justify-center mb-1">
              <TrendingUp className="w-4 h-4 text-purple-600" />
            </div>
            <p className="text-xl font-bold text-gray-900">
              {Math.round(output.aiResponse.metrics.relevance * 100)}%
            </p>
            <p className="text-xs text-gray-600">Relevance</p>
            {output.aiResponse.metrics.relevance_justification && (
              <details className="mt-2">
                <summary className="text-xs text-purple-700 cursor-pointer hover:text-purple-900">
                  Why?
                </summary>
                <p className="mt-1 text-xs text-gray-700 text-left bg-white p-2 rounded border border-purple-200">
                  {output.aiResponse.metrics.relevance_justification.substring(0, 100)}...
                </p>
              </details>
            )}
          </div>
        </div>

        {/* Additional Metrics */}
        <div className="flex items-center justify-between text-sm text-gray-600 mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-1">
            <CheckCircle className="w-4 h-4" />
            <span>Confidence: {Math.round(output.aiResponse.metrics.confidence_score * 100)}%</span>
          </div>
          <div className="flex items-center space-x-1">
            <FileText className="w-4 h-4" />
            <span>{output.aiResponse.metrics.sources_used} sources</span>
          </div>
        </div>

        {/* Toggle Details Button */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-center py-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="w-4 h-4 mr-1" />
              Show Less
            </>
          ) : (
            <>
              <ChevronDown className="w-4 h-4 mr-1" />
              View Full Details
            </>
          )}
        </button>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50 p-6 space-y-6">
          {/* Full Metrics */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Complete Evaluation Metrics</h4>
            <div className="space-y-4 text-sm">
              {/* Groundedness */}
              <div className="p-4 bg-white rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-700 flex items-center">
                    <Shield className="w-4 h-4 mr-2 text-blue-600" />
                    Groundedness
                  </span>
                  <span className="font-bold text-gray-900">
                    {Math.round(output.aiResponse.metrics.groundedness * 100)}%
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-2">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${output.aiResponse.metrics.groundedness * 100}%` }}
                  />
                </div>
                {output.aiResponse.metrics.groundedness_justification && (
                  <p className="text-xs text-gray-700 mt-2 p-2 bg-blue-50 rounded border border-blue-200 whitespace-pre-wrap">
                    {output.aiResponse.metrics.groundedness_justification}
                  </p>
                )}
              </div>

              {/* Accuracy */}
              <div className="p-4 bg-white rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-700 flex items-center">
                    <Target className="w-4 h-4 mr-2 text-green-600" />
                    Accuracy
                  </span>
                  <span className="font-bold text-gray-900">
                    {Math.round(output.aiResponse.metrics.accuracy * 100)}%
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-2">
                  <div
                    className="h-full bg-green-500 rounded-full"
                    style={{ width: `${output.aiResponse.metrics.accuracy * 100}%` }}
                  />
                </div>
                {output.aiResponse.metrics.accuracy_justification && (
                  <p className="text-xs text-gray-700 mt-2 p-2 bg-green-50 rounded border border-green-200 whitespace-pre-wrap">
                    {output.aiResponse.metrics.accuracy_justification}
                  </p>
                )}
              </div>

              {/* Relevance */}
              <div className="p-4 bg-white rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-700 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-2 text-purple-600" />
                    Relevance
                  </span>
                  <span className="font-bold text-gray-900">
                    {Math.round(output.aiResponse.metrics.relevance * 100)}%
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-2">
                  <div
                    className="h-full bg-purple-500 rounded-full"
                    style={{ width: `${output.aiResponse.metrics.relevance * 100}%` }}
                  />
                </div>
                {output.aiResponse.metrics.relevance_justification && (
                  <p className="text-xs text-gray-700 mt-2 p-2 bg-purple-50 rounded border border-purple-200 whitespace-pre-wrap">
                    {output.aiResponse.metrics.relevance_justification}
                  </p>
                )}
              </div>

              {/* Confidence */}
              <div className="p-4 bg-white rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-700">Confidence</span>
                  <span className="font-bold text-gray-900">
                    {Math.round(output.aiResponse.metrics.confidence_score * 100)}%
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-indigo-500 rounded-full"
                    style={{ width: `${output.aiResponse.metrics.confidence_score * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Agent Outputs */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Agent Outputs</h4>
            <div className="space-y-3">
              <details className="group">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                  Agent 1: Raw Processing
                </summary>
                <div className="mt-2 p-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-700">
                  {output.aiResponse.agent_1_output}
                </div>
              </details>

              <details className="group">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                  Agent 2: Summarization
                </summary>
                <div className="mt-2 p-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-700">
                  {output.aiResponse.agent_2_output}
                </div>
              </details>

              <details className="group">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                  Agent 3: Evaluation Reasoning
                </summary>
                <div className="mt-2 p-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-700">
                  {output.aiResponse.agent_3_output || 'No evaluation reasoning available (this output was generated before Agent 3 logging was implemented)'}
                </div>
              </details>
            </div>
          </div>

          {/* Sections Used */}
          {output.aiResponse.sections_used && output.aiResponse.sections_used.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Sections Used</h4>
              <div className="space-y-2">
                {output.aiResponse.sections_used.map((section, idx) => (
                  <div key={idx} className="p-3 bg-white rounded-lg border border-gray-200 text-sm">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-gray-700">{section.file}</span>
                      <span className="text-xs text-gray-500">Page {section.page}</span>
                    </div>
                    <p className="text-gray-600 text-xs line-clamp-2">{section.text_snippet}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Files Used */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Files Processed</h4>
            <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
              {output.files.map((file, idx) => (
                <li key={idx}>{file}</li>
              ))}
            </ul>
          </div>

          {/* Prompt Used */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Prompt Used</h4>
            <div className="p-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-700">
              {output.prompt}
            </div>
          </div>

          {/* Additional Context */}
          {output.additionalContextUsed && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Additional Context</h4>
              <div className="p-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-700 max-h-60 overflow-y-auto">
                <pre className="whitespace-pre-wrap">{output.additionalContextUsed}</pre>
              </div>
            </div>
          )}

          {/* Timestamp */}
          <div className="text-xs text-gray-500 pt-3 border-t border-gray-200">
            Created: {formatDate(output.createdAt)}
          </div>
        </div>
      )}
    </div>
  );
}
