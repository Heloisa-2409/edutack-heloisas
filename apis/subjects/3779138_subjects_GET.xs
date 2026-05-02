// Query subjects records owned by the authenticated user within their account
query subjects verb=GET {
  api_group = "subjects"
  auth = "user"

  input {
    // Page number for pagination
    int page?=1 filters=min:1
  
    // Number of items per page (max 100)
    int per_page?=30 filters=min:1|max:100
  }

  stack {
    db.query subjects {
      where = $db.subjects.user_id == $auth.id && $db.subjects.account_id == $auth.account_id
      return = {
        type  : "list"
        paging: {page: $input.page, per_page: $input.per_page}
      }
    } as $subjects_records
  }

  response = $subjects_records
}