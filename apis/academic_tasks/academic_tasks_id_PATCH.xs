query "academic_tasks/{id}" verb=PATCH {
  api_group = "academic_tasks"
  description = "Update a specific academic task by ID for the authenticated user"
  auth = "user"

  input {
    int id {
      description = "ID of the academic task"
    }

    int subject_id? {
      description = "Optional new subject ID"
    }

    text title? filters=trim {
      description = "Optional new title"
    }

    text description? filters=trim {
      description = "Optional new description"
    }

    date due_date? {
      description = "Optional new due date"
    }

    text status? filters=trim {
      description = "Optional new status"
    }
  }

  stack {
    // 1. Get the task and fail if it doesn't exist
    db.query "academic_tasks" {
      where = $db.academic_tasks.id == $input.id
      return = {type: "firstOrFail"}
    } as $existing_task

    // 2. Validate ownership
    precondition ($existing_task.user_id == $auth.id) {
      description = "Validate that the task belongs to the authenticated user"
      error_type = "accessdenied"
      error = "Access denied."
    }

    // 3. If subject_id is being updated, validate it
    conditional {
      if ($input.subject_id != null) {
        db.query "subjects" {
          where = $db.subjects.id == $input.subject_id && $db.subjects.user_id == $auth.id
          return = {type: "count"}
        } as $subject_count
        precondition (($subject_count > 0)) {
          description = "Validate that the new subject exists and belongs to the authenticated user"
          error_type = "inputerror"
          error = "Subject not found or does not belong to you."
        }
      }
    }

    // 4. If due_date is being updated, validate it's not in the past
    conditional {
      if ($input.due_date != null) {
        precondition ($input.due_date >= now|to_date) {
          description = "Validate that new due date is not in the past"
          error_type = "inputerror"
          error = "Due date cannot be in the past."
        }
      }
    }

    // 5. Prepare update data, including only non-null fields
    var $update_data {
      value = {
        subject_id: $input.subject_id,
        title: $input.title,
        description: $input.description,
        due_date: $input.due_date,
        status: $input.status
      }
    }
    var.update $update_data {
      value = $update_data|only_not_null
    }

    // 6. Ensure at least one field is being updated
    precondition (($update_data|count) > 0) {
      description = "Validate that at least one field is being updated"
      error_type = "inputerror"
      error = "No fields provided for update."
    }

    // 7. Perform the update
    db.update "academic_tasks" {
      id = $input.id
      data = $update_data
    } as $updated_task
  }

  response = $updated_task
}