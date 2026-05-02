// Create a new subject for the authenticated user
query subjects verb=POST {
  api_group = "subjects"
  auth = "user"

  input {
    text name filters=trim
    text description? filters=trim
  }

  stack {
    db.add subjects {
      data = {
        name       : $input.name
        description: $input.description
        user_id    : $auth.id
        account_id : $auth.account_id
      }
    } as $subject
  }

  response = $subject
}