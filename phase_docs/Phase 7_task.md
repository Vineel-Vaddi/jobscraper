# JobTailor Phase 7: Polish — Tasks

## Schema & Models
- [x] Extend `JobSearchSession` with saved/archive fields
- [x] Add `ProfilePreference` model
- [x] Add `RolePreset` model
- [x] Add `ResumePin` model (with pin modes: soft/strong/locked_if_supported)
- [x] Create Alembic migration

## Backend Services
- [x] Implement `titles_engine.py` (suggested target titles)
- [x] Implement `snippets_engine.py` (cover note snippets)

## Backend API Routes
- [x] Add saved session endpoints (save/archive)
- [x] Add profile preferences endpoints
- [x] Add role presets CRUD endpoints
- [x] Add resume pins CRUD endpoints
- [x] Add resume history endpoint
- [x] Add suggested titles endpoint
- [x] Add snippet generation endpoint
- [x] Update shared types + Pydantic schemas

## Frontend
- [x] Resume History page
- [x] Saved Sessions UI
- [x] Profile Preferences page
- [x] Role Presets UI
- [x] Pinning UI
- [x] Suggested Titles card
- [x] Cover Note Snippets card on review page

## Integration & Tests
- [x] Unit tests for titles, snippets, pin logic
