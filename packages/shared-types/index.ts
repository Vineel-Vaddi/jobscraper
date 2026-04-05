export type DocumentType = 'resume' | 'linkedin_pdf' | 'linkedin_export';
export type ParseStatus = 'pending' | 'processing' | 'success' | 'failed';

export interface UserResponse {
  id: number;
  display_name: string | null;
  email: string | null;
}

export interface DocumentResponse {
  id: number;
  document_type: DocumentType | string;
  original_filename: string;
  file_size: number;
  upload_status: string;
  parse_status: ParseStatus;
  parse_error_code?: string;
  parse_error_message?: string;
  created_at: string;
}

export interface DocumentEventResponse {
  type: string;
  details: string;
  created_at: string;
}

export interface DocumentDetailsResponse {
  document: {
    id: number;
    original_filename: string;
    document_type: string;
    parse_status: string;
    parse_error_code?: string;
    parse_error_message?: string;
  };
  extracted_text_url: string | null;
  events: DocumentEventResponse[];
}

export interface ProfileResponse {
  id: number;
  status: 'pending' | 'building' | 'success' | 'failed';
  canonical_profile_json?: Record<string, any>;
  confidence_summary_json?: Record<string, any>;
  merged_from_document_ids?: number[];
}

export interface JobSearchSessionResponse {
  id: number;
  status: 'pending' | 'processing' | 'success' | 'failed';
  source_url: string;
  source_type: string;
  ingest_error_code?: string;
  ingest_error_message?: string;
  raw_result_count: number;
  normalized_result_count: number;
  deduped_result_count: number;
  created_at: string;
}

export interface JobResponse {
  id: number;
  job_search_session_id: number;
  external_job_id?: string;
  source_type: string;
  source_job_url: string;
  canonical_job_url?: string;
  
  title: string;
  company: string;
  location?: string;
  work_mode?: string;
  employment_type?: string;
  seniority?: string;
  
  posted_at_raw?: string;
  posted_at_normalized?: string;
  
  description_text?: string;
  requirements_json?: Record<string, any>;
  metadata_json?: Record<string, any>;
  
  normalization_confidence?: string;
  fit_score?: number;
  fit_reasons_json?: string[];
  fit_gaps_json?: string[];
  
  created_at: string;
}
