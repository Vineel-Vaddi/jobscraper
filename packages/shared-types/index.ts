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
