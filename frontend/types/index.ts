// TypeScript interfaces matching backend JSON schemas

export interface RuntimeJSON {
  request_id?: string;
  file_paths: string[];
  prompt: string;
  timestamp?: string;
}

export interface SectionUsed {
  file: string;
  page: number;
  text_snippet: string;
}

export interface Metrics {
  confidence_score: number;              // 0-1 Confidence in the answer
  groundedness: number;                  // 0-1 Claims based on reliable data sources
  groundedness_justification: string;    // Detailed justification for groundedness score
  accuracy: number;                      // 0-1 Correctness of the response
  accuracy_justification: string;        // Detailed justification for accuracy score
  relevance: number;                     // 0-1 Pertinence to user's query
  relevance_justification: string;       // Detailed justification for relevance score
  sources_used: number;                  // Number of document sources used
  overall_score: number;                 // 0-1 Average of groundedness, accuracy, relevance
  needs_review: boolean;                 // True if overall_score < 0.8
}

export interface AIResponse {
  request_id: string;
  agent_1_output: string;
  agent_2_output: string;
  agent_3_output?: string;  // Optional for backward compatibility
  final_answer: string;
  metrics: Metrics;
  sections_used: SectionUsed[];
  processing_time_seconds: number;
  timestamp: string;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  file_paths: string[];
  count: number;
}

export type ProcessingStatus = "idle" | "uploading" | "processing" | "complete" | "error";

// Dynamic Element Configuration
export interface AdditionalContext {
  elementId: string;          // Reference to another element
  useLatestOutput: boolean;   // Use most recent run of that element
}

export interface DynamicElement {
  id: string;
  name: string;
  description: string;
  fileType: 'pdf';            // Extensible for future types
  prompt: string;
  additionalContext: AdditionalContext[];
  createdAt: string;          // ISO timestamp
  updatedAt: string;          // ISO timestamp
}

export interface SavedOutput {
  id: string;
  elementId: string;          // Link to parent element
  elementName: string;        // Snapshot of element name
  files: string[];            // File names used
  prompt: string;             // Snapshot of prompt used
  additionalContextUsed: string; // Combined context from other elements
  aiResponse: AIResponse;     // Full AI response + metrics
  createdAt: string;          // ISO timestamp
}
