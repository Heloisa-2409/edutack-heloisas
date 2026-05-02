// Delete a subject by ID, checking ownership
// Delete a subject by ID, ensuring the authenticated user owns it
query "subjects/{subjects_id}" verb=DELETE {
  api_group = "subjects"
  auth = "user"

  input {
    // The ID of the subject to delete
    int subjects_id filters=min:1
  }

  stack {
    // First check ownership
    db.get subjects {
      field_name = "id"
      field_value = $input.subjects_id
    } as $existing
  
    // Check if subject exists
    precondition ($existing == null) {
      error_type = "notfound"
      error = "Subject not found"
    }
  
    // Check ownership
    precondition ($existing.user_id != $auth.id || $existing.account_id != $auth.account_id) {
      error_type = "accessdenied"
      error = "Unauthorized: You can only delete your own subjects"
    }
  
    // Delete the record
    db.del subjects {
      field_name = "id"
      field_value = $input.subjects_id
    }
  }

  response = null
}