from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    linkedin_sub = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, index=True, nullable=True)
    display_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    job_sessions = relationship("JobSearchSession", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, index=True) # UUID string
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="sessions")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_type = Column(String, index=True) # e.g. resume, linkedin_pdf, linkedin_export
    original_filename = Column(String)
    mime_type = Column(String)
    file_size = Column(Integer)
    storage_key = Column(String, unique=True, index=True)
    
    upload_status = Column(String, default="pending") # pending, uploaded, failed
    parse_status = Column(String, default="pending") # pending, processing, success, failed
    
    parse_error_code = Column(String, nullable=True)
    parse_error_message = Column(Text, nullable=True)
    extracted_text_path = Column(String, nullable=True)
    parser_confidence = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="documents")
    parse_events = relationship("DocumentParseEvent", back_populates="document", cascade="all, delete-orphan")

class DocumentParseEvent(Base):
    __tablename__ = "document_parse_events"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    event_type = Column(String) # e.g. started, finished, failed
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="parse_events")

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    status = Column(String, default="pending") # pending, building, success, failed
    canonical_profile_json = Column(Text, nullable=True) # JSON stored as Text
    merged_from_document_ids = Column(Text, nullable=True) # JSON Array
    confidence_summary_json = Column(Text, nullable=True) # JSON
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="profile")

class JobSearchSession(Base):
    __tablename__ = "job_search_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    source_url = Column(String)
    source_type = Column(String, default="linkedin_search_url")
    status = Column(String, default="pending") # pending, processing, success, failed
    ingest_error_code = Column(String, nullable=True)
    ingest_error_message = Column(Text, nullable=True)
    
    raw_result_count = Column(Integer, default=0)
    normalized_result_count = Column(Integer, default=0)
    deduped_result_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="job_sessions")
    jobs = relationship("Job", back_populates="session", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_search_session_id = Column(Integer, ForeignKey("job_search_sessions.id"))
    
    external_job_id = Column(String, nullable=True, index=True)
    source_type = Column(String)
    source_job_url = Column(String)
    canonical_job_url = Column(String, nullable=True)
    
    title = Column(String)
    company = Column(String)
    location = Column(String, nullable=True)
    work_mode = Column(String, nullable=True) # onsite, hybrid, remote, unknown
    employment_type = Column(String, nullable=True) # full-time, contract, etc.
    seniority = Column(String, nullable=True)
    
    posted_at_raw = Column(String, nullable=True)
    posted_at_normalized = Column(DateTime(timezone=True), nullable=True)
    
    description_text = Column(Text, nullable=True)
    requirements_json = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    
    normalization_confidence = Column(String, nullable=True)
    dedupe_key = Column(String, nullable=True, index=True)
    
    fit_score = Column(Integer, nullable=True) # 0 to 100
    fit_reasons_json = Column(Text, nullable=True)
    fit_gaps_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="jobs")
    session = relationship("JobSearchSession", back_populates="jobs")
