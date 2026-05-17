query "subjects/{subjects_id}" verb=GET {
  api_group = "subjects"
  description = "Obtém uma disciplina específica pelo ID."
  auth = "user"

  input {
    int subjects_id {
      description = "ID da disciplina"
    }
  }

  stack {
    // 1. Buscar o registro
    db.query "subjects" {
      where = $db.subjects.id == $input.subjects_id
      return = {
        type: "firstOrFail"
      }
    } as $subject

    // 2. Verificar a Propriedade
    precondition ($subject.user_id == $auth.id && $subject.account_id == $auth.account_id) {
      error_type = "accessdenied"
      error = "Você não tem permissão para acessar este recurso."
    }
  }

  response = $subject
}