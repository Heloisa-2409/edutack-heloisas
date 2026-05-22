table subjects {
  auth = false

  schema {
    // Unique identifier for the subject
    int id

    // Timestamp when the subject was created
    timestamp created_at?=now

    // Name of the academic subject
    text name filters=trim

    // Optional description of the subject
    text description? filters=trim

    // Name of the professor/instructor
    text professor? filters=trim

    // Day of the week the class occurs
    text day_of_week?

    // Weekly workload in hours
    int carga_horaria?=0

    // ID of the user who owns the subject
    int user_id {
      table = "user"
    }

    // ID of the account associated with the subject
    int account_id {
      table = "account"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "user_id", op: "asc"}]}
  ]
}