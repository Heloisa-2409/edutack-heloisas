// Create a new academic task for the authenticated user
query academic_tasks verb=POST {
  api_group = "academic_tasks"
  auth = "user"

  input {
    // ID of the subject this task belongs to
    int subject_id
  
    // Title of the academic task
    text title filters=trim
  
    // Optional description of the task
    text description? filters=trim
  
    // Due date for the task
    date due_date
  
    // Status of the task (default: pending)
    text status?=pending filters=trim
  }

  stack {
    // Validate that subject_id exists and belongs to the user
    db.query subjects {
      where = $db.subjects.id == $input.subject_id && $db.subjects.user_id == $auth.id
      return = {type: "count"}
    } as $subject_count
  
    // Validate that the subject exists and belongs to the authenticated user
    precondition (($subject_count > 0)) {
      error_type = "inputerror"
      error = "Subject not found or does not belong to you."
    }
  
    // Validate due_date is not in the past
    // Validate that due date is not in the past
    precondition ($input.due_date >= (now|to_date)) {
      error_type = "inputerror"
      error = "Due date cannot be in the past."
    }
  
    db.add academic_tasks {
      data = {
        user_id    : $auth.id
        subject_id : $input.subject_id
        title      : $input.title
        description: $input.description
        due_date   : $input.due_date
        status     : $input.status
        created_at : now
      }
    } as $new_task
  }

  response = $new_task
}