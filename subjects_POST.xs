query "subjects" verb=POST {
  api_group = "subjects"
  description = "Cria uma nova disciplina para o usuário autenticado."
  auth = "user"

  input {
    text name {
      description = "Nome da disciplina"
    }
    text professor {
      description = "Nome do professor"
    }
    text day_of_week {
      description = "Dia da semana da aula"
    }
  }

  stack {
    var $new_subject {
      value = {
        name: $input.name,
        professor: $input.professor,
        day_of_week: $input.day_of_week,
        user_id: $auth.id,
        account_id: $auth.account_id
      }
    }

    db.insert "subjects" {
      data = $new_subject
    } as $created_subject
  }

  response = $created_subject
}