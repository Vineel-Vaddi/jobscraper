# Phase 5: Review, Diff, and Apply Launcher
This phase implemented the review integration interface between the backend logic models generating tailored outputs and the end-user applying to target roles. It successfully bridges transparent trust mechanisms for candidates before safely routing them to application sites alongside background lifecycle event logging.

## 1. What was Built
- **DB Events Modeler:** An abstracted `ApplyEvent` table capturing timestamped interactions ranging from simple PDF downloads up through explicitly verified `go_apply_clicked` triggers.
- **Diff Engine Layer:** A real-time structured API boundary that accepts the core static JSON format of Canonical Profiles and maps it explicitly against generated variant variants resolving visual differences at a granular UI level.
- **Why-Changed Explanations:** Connected deterministic rationale text bridging the skill gap validator into human-readable warnings and validation signals.
- **Review UI Hub:** Shifted the Tailor Result page (`tailor/[variantId]/page.tsx`) into an interactive "Master vs Variant" dashboard that groups changes logically before passing responsibility to the Applicant.

---
## 2. Schema Summary
Added `ApplyEvent` table scaling generic event telemetry directly to targeted resume actions.
**Key Columns:** `id`, `user_id`, `job_id`, `resume_variant_id`, `event_type`, `target_url`, `metadata_json`.

Added Pydantic schemas standardizing `SectionDiff` arrays wrapping `BulletDiff` payloads.

---
## 3. Diff Logic Summary
The `DiffEngine` executes iteratively using the backend's known baseline `Canonical Profile` against the specifically yielded Phase 4 JSON. It functions systematically:
1. **Sections:** Calculates string similarity differences inside `summary` blocks rendering `unchanged` vs `modified`. 
2. **Set Logic:** Resolves lists inside `skills` determining explicitly inserted string representations via Set Diff logic to output explicit `added` bullets.
3. **Array Boundaries:** Maps matching strings inside nested object arrays (like Experience blocks), asserting whether an explicit sub-string matches the baseline structure natively, identifying deterministic `rewritten` strings.

---
## 4. Why-Changed Note Summary
The `WhyChanged` model deterministically formats warning and transparency arrays using simple conditional checking on `SkillAnalyzer` arrays. If the engine sees a newly inserted valid string aligning with a documented JD skill, it produces: *“Emphasized the following skills across Summary and Skills sections because they align directly with the Job Description and are supported by your Canonical Profile..."*

---
## 5. Apply Tracking Summary
All final lifecycle logic sits natively behind the `[variantId]/go-apply` action block. 
1. When triggering the event, the Backend looks up the target boundary (the `source_job_url` acquired during Phase 3).
2. It constructs an `ApplyEvent` indicating an opened target loop (`go_apply_clicked`).
3. Safely returns the literal URL payload back up to the UX allowing independent secure `_blank` invocation of the original portal.

---
## 6. Test Coverage Summary
Added Unit logic within `test_review.py` verifying deep JSON structure arrays parse safely:
- Reordered skills generate clean output.
- Missing and modified experience logic is successfully registered.
- Unsupported warning blocks are passed explicitly alongside 'Why Changed' validation tests.

---
## 7. What Remains for Phase 6
Phase 5 finishes the strict generation tracking lifecycle for simple operations. Moving into Phase 6:
- **Full History Timeline UI:** Building the application tracking UI mapping explicitly derived state off historical `ApplyEvent` timestamps.
- **Automated Stage Fetching:** Refreshing the application stages from external APIs tracking success loops autonomously.
