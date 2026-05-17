query "subjects/{subjects_id}" verb=DELETE {
  api_group = "subjects"
  description = "Deleta uma disciplina específica."
  auth = "user"

  input {
    int subjects_id {
      description = "ID da disciplina"
    }
  }

  stack {
    // 1. Lógica de Validação de Propriedade
    db.query "subjects" {
      where = $db.subjects.id == $input.subjects_id
      return = {
        type: "firstOrFail"
      }
    } as $subject

    precondition ($subject.user_id == $auth.id && $subject.account_id == $auth.account_id) {
      error_type = "accessdenied"
      error = "Você não tem permissão para deletar este recurso."
    }

    // 2. Deletar o registro
    db.delete "subjects" {
      id = $input.subjects_id
    } as $deleted_subject
  }

  response = $deleted_subject
}