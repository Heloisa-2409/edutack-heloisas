// List all academic tasks for the authenticated user
query academic_tasks verb=GET {
  api_group = "academic_tasks"
  auth = "user"

  input {
    // Page number for pagination
    int page?=1 filters=min:1
  
    // Number of items per page (max 100)
    int per_page?=10 filters=min:1|max:100
  
    // Optional status filter (pending, completed, etc.)
    text status? filters=trim
  }

  stack {
    var $where_conditions {
      value = $db.academic_tasks.user_id == $auth.id
    }
  
    conditional {
      if ($input.status != null) {
        var.update $where_conditions {
          value = $where_conditions && $db.academic_tasks.status == $input.status
        }
      }
    }
  
    db.query academic_tasks {
      where = $where_conditions == true
      sort = {academic_tasks.due_date: "asc"}
      return = {
        type  : "list"
        paging: {
          page    : $input.page
          per_page: $input.per_page
          totals  : true
        }
      }
    } as $tasks
  }

  response = $tasks
}