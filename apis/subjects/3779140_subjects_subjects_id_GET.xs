// Retrieve a subject by ID, checking ownership
// Retrieve a subject by ID, ensuring the authenticated user owns it
query "subjects/{subjects_id}" verb=GET {
  api_group = "subjects"
  auth = "user"

  input {
    // The ID of the subject to retrieve
    int subjects_id filters=min:1
  }

  stack {
    db.get subjects {
      field_name = "id"
      field_value = $input.subjects_id
    } as $record
  
    // Check if subject exists
    precondition ($record == null) {
      error_type = "notfound"
      error = "Subject not found"
    }
  
    // Check ownership
    precondition ($record.user_id != $auth.id || $record.account_id != $auth.account_id) {
      error_type = "accessdenied"
      error = "Unauthorized: You can only access your own subjects"
    }
  }

  response = $record
}