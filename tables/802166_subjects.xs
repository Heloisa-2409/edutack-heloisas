table subjects {
  auth = false

  schema {
    // Unique identifier for the subject
    // Unique identifier for the subject
    int id
  
    // Timestamp when the subject was created
    // Timestamp when the subject was created
    timestamp created_at?=now
  
    // Name of the academic subject
    // Name of the academic subject
    text name filters=trim
  
    // Optional description of the subject
    // Optional description of the subject
    text description? filters=trim
  
    // ID of the user who owns the subject
    // ID of the user who owns the subject
    int user_id {
      table = "user"
    }
  
    // ID of the account associated with the subject
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