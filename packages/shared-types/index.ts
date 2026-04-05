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

export interface ResumeVariantResponse {
  id: number;
  user_id: number;
  profile_id?: number;
  job_id?: number;
  base_document_id?: number;
  
  status: string; // pending, processing, success, failed, needs_review
  
  jd_summary_json?: Record<string, any>;
  keyword_alignment_json?: Record<string, any>;
  skill_gap_json?: Record<string, any>;
  tailored_resume_json?: Record<string, any>;
  tailored_resume_text?: string;
  validator_report_json?: Record<string, any>;
  ats_score_json?: Record<string, any>;
  
  error_code?: string;
  error_message?: string;
  
  created_at: string;
  updated_at?: string;
}

export interface AgentRunResponse {
  id: number;
  run_type: string;
  target_entity_type?: string;
  target_entity_id?: number;
  status: string;
  duration_ms?: number;
  error_code?: string;
  error_message?: string;
  started_at: string;
  finished_at?: string;
  metadata_json?: Record<string, any>;
}

export interface SystemSummaryResponse {
  total_jobs: number;
  total_variants: number;
  failed_runs: number;
  success_runs: number;
}

// ── Phase 7 ─────────────────────────────────────────────────

export interface ProfilePreferenceResponse {
  id: number;
  preferred_locations: string[];
  preferred_work_modes: string[];
  preferred_employment_types: string[];
  target_seniority?: string;
  preferred_industries: string[];
  salary_notes?: string;
  exclude_keywords: string[];
  resume_emphasis?: string;
}

export interface RolePresetResponse {
  id: number;
  name: string;
  target_titles: string[];
  priority_skills: string[];
  summary_focus?: string;
  created_at: string;
}

export interface ResumePinResponse {
  id: number;
  source_type: string;
  source_ref: string;
  label?: string;
  pin_mode: string;
  created_at: string;
}

export interface ResumeHistoryItem {
  id: number;
  job_title: string;
  company: string;
  status: string;
  ats_coverage?: number;
  validator_status?: string;
  applied: boolean;
  created_at: string;
  has_docx: boolean;
  has_pdf: boolean;
}

export interface SuggestedTitle {
  title: string;
  confidence: string;
  rationale: string;
}

export interface SnippetResponse {
  short_intro: string;
  why_fit: string;
  why_role: string;
  recruiter_note: string;
}
