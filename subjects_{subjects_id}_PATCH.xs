query "subjects/{subjects_id}" verb=PATCH {
  api_group = "subjects"
  description = "Atualiza uma disciplina específica."
  auth = "user"

  input {
    int subjects_id {
      description = "ID da disciplina"
    }
    text name? {
      description = "Novo nome da disciplina"
    }
    text professor? {
      description = "Novo nome do professor"
    }
    text day_of_week? {
      description = "Novo dia da semana"
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
      error = "Você não tem permissão para modificar este recurso."
    }

    // 2. Atualizar o registro
    db.update "subjects" {
      id = $input.subjects_id
      data = {
        name: $input.name,
        professor: $input.professor,
        day_of_week: $input.day_of_week
      }
    } as $updated_subject
  }

  response = $updated_subject
}