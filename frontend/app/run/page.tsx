'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { getElements, getElement, getLatestOutput, saveOutput } from '@/services/storage';
import { uploadFiles, processDocuments } from '@/services/api';
import { DynamicElement, AIResponse, ProcessingStatus as Status } from '@/types';
import FileUpload from '@/components/FileUpload';
import ProcessingStatus from '@/components/ProcessingStatus';
import ResultsDisplay from '@/components/ResultsDisplay';
import { Check, ArrowRight, ArrowLeft, Play, Save, Home } from 'lucide-react';
import Link from 'next/link';

type Step = 1 | 2 | 3 | 4;

export default function RunPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [currentStep, setCurrentStep] = useState<Step>(1);
  const [elements, setElements] = useState<DynamicElement[]>([]);
  const [selectedElement, setSelectedElement] = useState<DynamicElement | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [status, setStatus] = useState<Status>('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const [result, setResult] = useState<AIResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [additionalContextText, setAdditionalContextText] = useState('');

  useEffect(() => {
    const allElements = getElements();
    setElements(allElements);

    // Check if an element is pre-selected via URL
    const elementId = searchParams.get('elementId');
    if (elementId) {
      const element = getElement(elementId);
      if (element) {
        setSelectedElement(element);
        setCurrentStep(2);
      }
    }
  }, [searchParams]);

  const loadAdditionalContext = async () => {
    if (!selectedElement) return '';

    const contexts: string[] = [];

    for (const context of selectedElement.additionalContext) {
      if (context.useLatestOutput) {
        const latestOutput = getLatestOutput(context.elementId);
        if (latestOutput) {
          const contextElement = getElement(context.elementId);
          contexts.push(
            `\n--- Context from "${contextElement?.name}" ---\n${latestOutput.aiResponse.final_answer}\n`
          );
        }
      }
    }

    return contexts.join('\n');
  };

  const handleNext = async () => {
    if (currentStep === 1 && selectedElement) {
      setCurrentStep(2);
    } else if (currentStep === 2 && files.length > 0) {
      // Load additional context before moving to preview
      const contextText = await loadAdditionalContext();
      setAdditionalContextText(contextText);
      setCurrentStep(3);
    } else if (currentStep === 3) {
      await handleExecute();
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((currentStep - 1) as Step);
      setError(null);
    }
  };

  const handleExecute = async () => {
    if (!selectedElement) return;

    try {
      setError(null);
      setResult(null);

      // Step 1: Upload files
      setStatus('uploading');
      setStatusMessage(`Uploading ${files.length} file(s)...`);

      const uploadResponse = await uploadFiles(files);

      // Step 2: Process documents
      setStatus('processing');
      setStatusMessage('AI agents are analyzing your documents...');

      // Combine prompt with additional context
      const fullPrompt = additionalContextText
        ? `${selectedElement.prompt}\n\nAdditional Context:\n${additionalContextText}`
        : selectedElement.prompt;

      const runtimeJson = {
        file_paths: uploadResponse.file_paths,
        prompt: fullPrompt,
      };

      const aiResponse = await processDocuments(runtimeJson);

      // Step 3: Show results
      setStatus('complete');
      setStatusMessage('Processing complete!');
      setResult(aiResponse);
      setCurrentStep(4);

    } catch (err: any) {
      console.error('Error:', err);
      setStatus('error');
      setError(err.response?.data?.detail || err.message || 'An error occurred during processing');
      setStatusMessage('');
    }
  };

  const handleSaveOutput = () => {
    if (!selectedElement || !result) return;

    saveOutput({
      elementId: selectedElement.id,
      elementName: selectedElement.name,
      files: files.map(f => f.name),
      prompt: selectedElement.prompt,
      additionalContextUsed: additionalContextText,
      aiResponse: result,
    });

    alert('Output saved successfully!');
    router.push('/outputs');
  };

  const handleRunAgain = () => {
    setFiles([]);
    setStatus('idle');
    setStatusMessage('');
    setResult(null);
    setError(null);
    setAdditionalContextText('');
    setCurrentStep(2);
  };

  const isNextDisabled = () => {
    if (currentStep === 1) return !selectedElement;
    if (currentStep === 2) return files.length === 0;
    return false;
  };

  const isProcessing = status === 'uploading' || status === 'processing';

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Run Element</h1>
          <p className="text-gray-600">
            Execute a dynamic element with your documents
          </p>
        </div>

        {/* Step Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {[1, 2, 3, 4].map((step) => (
              <div key={step} className="flex items-center flex-1">
                <div className="flex items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                      step < currentStep
                        ? 'bg-green-500 text-white'
                        : step === currentStep
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {step < currentStep ? <Check className="w-5 h-5" /> : step}
                  </div>
                  <div className="ml-3 hidden sm:block">
                    <p
                      className={`text-sm font-medium ${
                        step <= currentStep ? 'text-gray-900' : 'text-gray-500'
                      }`}
                    >
                      {step === 1 && 'Select'}
                      {step === 2 && 'Upload'}
                      {step === 3 && 'Preview'}
                      {step === 4 && 'Results'}
                    </p>
                  </div>
                </div>
                {step < 4 && (
                  <div
                    className={`h-1 flex-1 mx-4 rounded ${
                      step < currentStep ? 'bg-green-500' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-6">
          {/* Step 1: Select Element */}
          {currentStep === 1 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Select an Element
              </h2>
              {elements.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-600 mb-4">
                    No elements available. Create one first.
                  </p>
                  <Link
                    href="/elements?create=true"
                    className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  >
                    Create Element
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {elements.map((element) => (
                    <button
                      key={element.id}
                      onClick={() => setSelectedElement(element)}
                      className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                        selectedElement?.id === element.id
                          ? 'border-blue-600 bg-blue-50'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                      }`}
                    >
                      <h3 className="font-semibold text-gray-900 mb-1">
                        {element.name}
                      </h3>
                      {element.description && (
                        <p className="text-sm text-gray-600 mb-2">
                          {element.description}
                        </p>
                      )}
                      <p className="text-sm text-gray-700 line-clamp-2">
                        <span className="font-medium">Prompt:</span> {element.prompt}
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 2: Upload Files */}
          {currentStep === 2 && selectedElement && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Upload Documents
              </h2>
              <p className="text-gray-600 mb-6">
                For element: <span className="font-semibold">{selectedElement.name}</span>
              </p>
              <FileUpload onFilesSelected={setFiles} disabled={isProcessing} />
            </div>
          )}

          {/* Step 3: Preview Configuration */}
          {currentStep === 3 && selectedElement && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Preview Configuration
              </h2>

              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Element</h3>
                  <p className="text-lg font-semibold text-gray-900">{selectedElement.name}</p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Prompt</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-900">{selectedElement.prompt}</p>
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Files to Process</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {files.map((file, idx) => (
                      <li key={idx} className="text-gray-700">{file.name}</li>
                    ))}
                  </ul>
                </div>

                {additionalContextText && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Additional Context</h3>
                    <div className="bg-blue-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                      <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                        {additionalContextText}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 4: Results */}
          {currentStep === 4 && (
            <div>
              {status !== 'idle' && status !== 'complete' && (
                <ProcessingStatus status={status} message={statusMessage} />
              )}

              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <h3 className="text-red-800 font-semibold mb-2">Error</h3>
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}

              {result && status === 'complete' && (
                <>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Results</h2>
                    <button
                      onClick={handleSaveOutput}
                      className="flex items-center px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                    >
                      <Save className="w-4 h-4 mr-2" />
                      Save Output
                    </button>
                  </div>
                  <ResultsDisplay result={result} />
                </>
              )}
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        {currentStep < 4 && (
          <div className="flex items-center justify-between">
            <button
              onClick={handleBack}
              disabled={currentStep === 1}
              className={`flex items-center px-6 py-3 border border-gray-300 rounded-lg font-medium transition-colors ${
                currentStep === 1
                  ? 'opacity-50 cursor-not-allowed text-gray-400'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </button>

            <button
              onClick={handleNext}
              disabled={isNextDisabled() || isProcessing}
              className={`flex items-center px-6 py-3 rounded-lg font-medium transition-all ${
                isNextDisabled() || isProcessing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md'
              }`}
            >
              {currentStep === 3 ? (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Execute
                </>
              ) : (
                <>
                  Next
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </button>
          </div>
        )}

        {/* Results Actions */}
        {currentStep === 4 && result && (
          <div className="flex items-center justify-center space-x-4">
            <button
              onClick={handleRunAgain}
              className="flex items-center px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              <Play className="w-4 h-4 mr-2" />
              Run Again
            </button>
            <Link
              href="/"
              className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Home className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
