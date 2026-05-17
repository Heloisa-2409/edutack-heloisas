// Delete a specific academic task by ID for the authenticated user
query "academic_tasks/{id}" verb=DELETE {
  api_group = "academic_tasks"
  auth = "user"

  input {
    // ID of the academic task to delete
    int id
  }

  stack {
    // First, verify the task exists and belongs to the user
    db.query academic_tasks {
      where = $db.academic_tasks.id == $input.id && $db.academic_tasks.user_id == $auth.id
      return = {type: "count"}
    } as $task_count
  
    // Validate that the task exists and belongs to the authenticated user
    precondition (($task_count > 0)) {
      error_type = "accessdenied"
      error = "Task not found or access denied."
    }
  
    // Delete the task
    db.del academic_tasks {
      field_name = "id"
      field_value = $input.id
    }
  }

  response = {success: true, message: "Task deleted successfully"}
}