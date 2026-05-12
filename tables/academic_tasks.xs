table "academic_tasks" {
  auth = false
  schema {
    int id {
      description = "Unique identifier for the academic task"
    }

    int user_id {
      table = "user"
      description = "ID of the user who owns the task"
    }

    int subject_id {
      table = "subjects"
      description = "ID of the subject this task belongs to"
    }

    text title filters=trim {
      description = "Title of the academic task"
    }

    text description? filters=trim {
      description = "Optional description of the task"
    }

    date due_date {
      description = "Due date for the task"
    }

    text status?="pending" {
      description = "Status of the task (e.g., pending, completed)"
    }

    timestamp created_at?=now {
      description = "Timestamp when the task was created"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "user_id"}]}
    {type: "btree", field: [{name: "subject_id"}]}
    {type: "btree", field: [{name: "due_date", op: "asc"}]}
    {type: "btree", field: [{name: "status", op: "asc"}]}
  ]
}