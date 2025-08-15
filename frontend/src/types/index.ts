export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  user_id: string;
  filename: string;
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;
  upload_status: string;
  processing_status: string;
  total_pages?: number;
  total_characters?: number;
  doc_metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  processed_at?: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  content_type: string;
  page_number?: number;
  character_count: number;
  word_count: number;
  embedding_id?: string;
  chunk_metadata?: Record<string, any>;
  created_at: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title?: string;
  is_active: boolean;
  document_filter: string[];
  system_prompt?: string;
  created_at: string;
  updated_at: string;
  last_message_at?: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  message_type: 'user' | 'assistant' | 'system';
  content: string;
  source_chunks: string[];
  token_usage?: Record<string, any>;
  model_used?: string;
  response_time_ms?: number;
  msg_metadata?: Record<string, any>;
  created_at: string;
}

export interface UserSettings {
  id: string;
  user_id: string;
  preferred_model: string;
  max_tokens: number;
  temperature: number;
  chunk_size: number;
  chunk_overlap: number;
  default_document_filter: string[];
  ui_preferences: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface QuestionRequest {
  question: string;
  session_id?: string;
  document_filter?: string[];
  use_history?: boolean;
}

export interface QuestionResponse {
  answer: string;
  sources: Array<{
    document_id: string;
    document_name: string;
    chunk_id: string;
    page_number?: number;
    similarity: number;
    content_preview: string;
  }>;
  session_id: string;
  message_id: string;
  token_usage?: Record<string, any>;
  response_time_ms: number;
}

export interface ProcessingStatus {
  document: {
    id: string;
    filename: string;
    upload_status: string;
    processing_status: string;
    total_pages?: number;
    total_characters?: number;
    processed_at?: string;
  };
  chunks: {
    total: number;
    with_embeddings: number;
    embedding_progress: number;
  };
  jobs: Array<{
    id: string;
    type: string;
    status: string;
    progress: number;
    error?: string;
    started_at?: string;
    completed_at?: string;
  }>;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}