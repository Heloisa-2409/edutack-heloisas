table academic_tasks {
  auth = false

  schema {
    // Unique identifier for the academic task
    int id
  
    // ID of the user who owns the task
    int user_id {
      table = "user"
    }
  
    // ID of the subject this task belongs to
    int subject_id {
      table = "subjects"
    }
  
    // Title of the academic task
    text title filters=trim
  
    // Optional description of the task
    text description? filters=trim
  
    // Due date for the task
    date due_date
  
    // Status of the task (e.g., pending, completed)
    text status?=pending
  
    // Timestamp when the task was created
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "user_id"}]}
    {type: "btree", field: [{name: "subject_id"}]}
    {type: "btree", field: [{name: "due_date", op: "asc"}]}
    {type: "btree", field: [{name: "status", op: "asc"}]}
  ]
}