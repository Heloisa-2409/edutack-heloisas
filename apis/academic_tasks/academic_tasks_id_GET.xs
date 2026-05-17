// Get a specific academic task by ID for the authenticated user
query "academic_tasks/{id}" verb=GET {
  api_group = "academic_tasks"
  auth = "user"

  input {
    // ID of the academic task
    int id
  }

  stack {
    db.query academic_tasks {
      where = $db.academic_tasks.id == $input.id && $db.academic_tasks.user_id == $auth.id
      return = {type: "single"}
    } as $task
  
    // Validate that the task exists and belongs to the authenticated user
    precondition ($task != null) {
      error_type = "accessdenied"
      error = "Task not found or access denied."
    }
  }

  response = $task
}