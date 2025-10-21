'use client';

import React from 'react';
import { AIResponse } from '@/types';
import { CheckCircle, AlertCircle, Clock, FileText, TrendingUp, Award, Shield, Target, AlertTriangle } from 'lucide-react';

interface ResultsDisplayProps {
  result: AIResponse;
}

export default function ResultsDisplay({ result }: ResultsDisplayProps) {
  // DEBUG: Log the full result to console
  console.log('='.repeat(80));
  console.log('DEBUG: ResultsDisplay received data:');
  console.log('Metrics:', result.metrics);
  console.log('Groundedness justification:', result.metrics.groundedness_justification);
  console.log('Accuracy justification:', result.metrics.accuracy_justification);
  console.log('Relevance justification:', result.metrics.relevance_justification);
  console.log('='.repeat(80));

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 0.8) return 'bg-green-50 border-green-200';
    if (score >= 0.6) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  return (
    <div className="w-full space-y-6 animate-in fade-in slide-in-from-bottom-4">
      {/* Warning Banner for Low Quality */}
      {result.metrics.needs_review && (
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-1">
                Quality Review Required
              </h3>
              <p className="text-sm text-red-700">
                This result has an overall quality score below 80%. Please review the metrics and consider re-running with additional context or refining the prompt.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Final Answer */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex items-start space-x-3 mb-4">
          <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Answer</h2>
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {result.final_answer}
            </p>
          </div>
        </div>
      </div>

      {/* Overall Quality Score - Prominent */}
      <div className={`rounded-lg border-2 p-6 ${getScoreBg(result.metrics.overall_score)}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Award className={`w-8 h-8 ${getScoreColor(result.metrics.overall_score)}`} />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Overall Quality Score</h3>
              <p className="text-sm text-gray-600">Average of Groundedness, Accuracy, and Relevance</p>
            </div>
          </div>
          <div className="text-right">
            <p className={`text-4xl font-bold ${getScoreColor(result.metrics.overall_score)}`}>
              {Math.round(result.metrics.overall_score * 100)}%
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {result.metrics.overall_score >= 0.8 ? 'Excellent' : result.metrics.overall_score >= 0.6 ? 'Good' : 'Needs Review'}
            </p>
          </div>
        </div>
      </div>

      {/* Evaluation Metrics */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" />
          Evaluation Metrics
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Groundedness */}
          <div className={`p-4 rounded-lg border-2 ${getScoreBg(result.metrics.groundedness)}`}>
            <div className="flex items-center space-x-2 mb-2">
              <Shield className="w-5 h-5 text-blue-600" />
              <p className="text-sm font-medium text-gray-700">Groundedness</p>
            </div>
            <p className={`text-3xl font-bold ${getScoreColor(result.metrics.groundedness)}`}>
              {Math.round(result.metrics.groundedness * 100)}%
            </p>
            <p className="text-xs text-gray-600 mt-1">Claims based on reliable sources</p>
            <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full transition-all"
                style={{ width: `${result.metrics.groundedness * 100}%` }}
              />
            </div>
            {/* Justification */}
            <details className="mt-3">
              <summary className="text-xs text-blue-700 cursor-pointer hover:text-blue-900 font-medium">
                View Justification
              </summary>
              <p className="mt-2 text-xs text-gray-700 bg-white p-2 rounded border border-blue-200 whitespace-pre-wrap">
                {result.metrics.groundedness_justification}
              </p>
            </details>
          </div>

          {/* Accuracy */}
          <div className={`p-4 rounded-lg border-2 ${getScoreBg(result.metrics.accuracy)}`}>
            <div className="flex items-center space-x-2 mb-2">
              <Target className="w-5 h-5 text-green-600" />
              <p className="text-sm font-medium text-gray-700">Accuracy</p>
            </div>
            <p className={`text-3xl font-bold ${getScoreColor(result.metrics.accuracy)}`}>
              {Math.round(result.metrics.accuracy * 100)}%
            </p>
            <p className="text-xs text-gray-600 mt-1">Correctness of the response</p>
            <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 rounded-full transition-all"
                style={{ width: `${result.metrics.accuracy * 100}%` }}
              />
            </div>
            {/* Justification */}
            <details className="mt-3">
              <summary className="text-xs text-green-700 cursor-pointer hover:text-green-900 font-medium">
                View Justification
              </summary>
              <p className="mt-2 text-xs text-gray-700 bg-white p-2 rounded border border-green-200 whitespace-pre-wrap">
                {result.metrics.accuracy_justification}
              </p>
            </details>
          </div>

          {/* Relevance */}
          <div className={`p-4 rounded-lg border-2 ${getScoreBg(result.metrics.relevance)}`}>
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              <p className="text-sm font-medium text-gray-700">Relevance</p>
            </div>
            <p className={`text-3xl font-bold ${getScoreColor(result.metrics.relevance)}`}>
              {Math.round(result.metrics.relevance * 100)}%
            </p>
            <p className="text-xs text-gray-600 mt-1">Pertinence to the query</p>
            <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-500 rounded-full transition-all"
                style={{ width: `${result.metrics.relevance * 100}%` }}
              />
            </div>
            {/* Justification */}
            <details className="mt-3">
              <summary className="text-xs text-purple-700 cursor-pointer hover:text-purple-900 font-medium">
                View Justification
              </summary>
              <p className="mt-2 text-xs text-gray-700 bg-white p-2 rounded border border-purple-200 whitespace-pre-wrap">
                {result.metrics.relevance_justification}
              </p>
            </details>
          </div>
        </div>

        {/* Additional Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {/* Confidence Score */}
          <div className="text-center p-4 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600 mb-1">Confidence</p>
            <p className={`text-2xl font-bold ${getScoreColor(result.metrics.confidence_score)}`}>
              {Math.round(result.metrics.confidence_score * 100)}%
            </p>
          </div>

          {/* Sources Used */}
          <div className="text-center p-4 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600 mb-1">Sources Used</p>
            <p className="text-2xl font-bold text-blue-600">
              {result.metrics.sources_used}
            </p>
          </div>

          {/* Processing Time */}
          <div className="text-center p-4 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600 mb-1">Processing Time</p>
            <p className="text-2xl font-bold text-gray-700">
              {result.processing_time_seconds.toFixed(1)}s
            </p>
          </div>
        </div>
      </div>

      {/* Sections Used */}
      {result.sections_used && result.sections_used.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2" />
            Document Sections Referenced
          </h3>

          <div className="space-y-3">
            {result.sections_used.map((section, index) => (
              <div
                key={index}
                className="p-4 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">
                    {section.file}
                  </span>
                  <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded">
                    Page {section.page}
                  </span>
                </div>
                <p className="text-sm text-gray-600 italic">
                  "{section.text_snippet}"
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agent Outputs (Collapsible/Optional) */}
      <details className="bg-white rounded-lg border border-gray-200 shadow-sm">
        <summary className="p-4 cursor-pointer hover:bg-gray-50 transition-colors font-medium text-gray-700">
          View Detailed Agent Outputs
        </summary>
        <div className="p-4 border-t border-gray-200 space-y-4">
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Agent 1 - Raw Output</h4>
            <p className="text-sm text-gray-600 whitespace-pre-wrap bg-gray-50 p-3 rounded">
              {result.agent_1_output}
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Agent 2 - Summarized Output</h4>
            <p className="text-sm text-gray-600 whitespace-pre-wrap bg-gray-50 p-3 rounded">
              {result.agent_2_output}
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Agent 3 - Evaluation Reasoning</h4>
            <p className="text-sm text-gray-600 whitespace-pre-wrap bg-gray-50 p-3 rounded">
              {result.agent_3_output || 'No evaluation reasoning available (this output was generated before Agent 3 logging was implemented)'}
            </p>
          </div>
        </div>
      </details>
    </div>
  );
}
