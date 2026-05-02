// Update a subject by ID, checking ownership
// Update a subject by ID, ensuring the authenticated user owns it
query "subjects/{subjects_id}" verb=PATCH {
  api_group = "subjects"
  auth = "user"

  input {
    // The ID of the subject to update
    int subjects_id filters=min:1
  
    // The new name for the subject
    text name? filters=trim
  
    // The new description for the subject
    text description? filters=trim
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
      error = "Unauthorized: You can only update your own subjects"
    }
  
    // Build update data
    var $update_data {
      value = {}
    }
  
    conditional {
      if ($input.name != null) {
        var.update $update_data {
          value = $update_data|set:"name":$input.name
        }
      }
    }
  
    conditional {
      if ($input.description != null) {
        var.update $update_data {
          value = $update_data
            |set:"description":$input.description
        }
      }
    }
  
    // Update the record
    db.patch subjects {
      field_name = "id"
      field_value = $input.subjects_id
      data = $update_data
    } as $updated
  }

  response = $updated
}