# feature-notas-atividades Proposal

## Why
- The current EduTrack AI backend has no persistent model for student grades or a dedicated endpoint for teachers to submit grades.
- This feature SHALL enable a professor to record a grade for a student on a specific academic activity while keeping the implementation scoped to grade creation only.
- The design MUST preserve the existing multi-tenant pattern by scoping writes to the authenticated user and their account.

## What Changes
- Add a new database table `activity_grades` to store grade submissions.
  - Fields: `id`, `created_at`, `updated_at`, `user_id`, `account_id`, `student_id`, `subject_id?`, `activity_id?`, `activity_name`, `grade`, `comments?`.
  - `user_id` SHALL represent the authenticated professor who created the grade record.
  - `student_id` SHALL reference the graded student user.
  - `subject_id` SHALL be optional to relate the grade to an existing `subjects` record.
  - `activity_id` SHALL be an optional numeric identifier for a specific activity when available.
  - `activity_name` SHALL capture the specific activity description.
  - `grade` SHALL be validated as a score within an acceptable academic range (e.g., 0-100).
- Add a new API endpoint `POST /activity_grades`.
  - Authenticated endpoint (`auth = "user"`).
  - Input parameters: `student_id`, `activity_name`, `grade`, optional `subject_id`, optional `activity_id`, optional `comments`.
  - The endpoint SHALL create a new `activity_grades` record scoped to `$auth.id` and `$auth.account_id`.
  - No list/query or GET endpoints SHALL be added, because the user requested only the ability to launch grades.
- Keep the scope strictly limited to the explicit requirement of grade submission.

## Impact
- Enables Streamlit frontend to submit student grades for specific activities.
- Maintains tenant isolation and user ownership using `account_id` and `user_id`.
- Leaves room for future expansion with activity entities or teacher-specific permission checks.
- Avoids adding extra read/list endpoints that are outside the requested scope.
