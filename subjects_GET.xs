query "subjects" verb=GET {
  api_group = "subjects"
  description = "Lista todas as disciplinas do usuário autenticado."
  auth = "user"

  stack {
    db.query "subjects" {
      where = $db.subjects.user_id == $auth.id && $db.subjects.account_id == $auth.account_id
      return = {
        type: "list"
      }
    } as $subjects
  }

  response = $subjects
}