# feature-subjects-crud Proposal

## Why
- The EduTrack AI backend needs a secure subjects CRUD API that keeps each user isolated to their own data.
- This feature SHALL prevent users from reading, updating, or deleting subjects they do not own.
- The design MUST preserve tenant isolation by enforcing both `user_id` and `account_id` ownership checks.

## What Changes
- Add or verify RESTful endpoints for the `subjects` resource:
  - `GET /subjects`
  - `POST /subjects`
  - `GET /subjects/{subjects_id}`
  - `PATCH /subjects/{subjects_id}`
  - `DELETE /subjects/{subjects_id}`
- Ensure each endpoint uses `auth = "user"`.
- Implement ownership enforcement on every operation:
  - `GET /subjects` SHALL filter by `$auth.id` and `$auth.account_id`.
  - `POST /subjects` SHALL create records with `user_id = $auth.id` and `account_id = $auth.account_id`.
  - The `{subjects_id}` endpoints SHALL verify the record exists and belongs to the authenticated user before returning, updating, or deleting it.
- Return clear error types for unauthorized or missing records:
  - `notfound` when the record does not exist
  - `accessdenied` when the record exists but is owned by another user or account

## Impact
- Provides a complete scoped CRUD interface for subject management.
- Protects user data via multi-tenant ownership checks.
- Enables frontend workflows to safely list, create, update, and remove subjects.
- Keeps the implementation narrow to the requested feature, without adding unrelated endpoints or broader access patterns.
