query "academic_tasks/{academic_tasks_id}" verb=PATCH {
  api_group = "academic_tasks"
  description = "Atualiza uma tarefa acadêmica específica do usuário autenticado."
  auth = "user"

  input {
    int academic_tasks_id {
      description = "ID da tarefa acadêmica a ser atualizada."
    }
    text title? {
      description = "Novo título da tarefa."
    }
    text description? {
      description = "Nova descrição da tarefa."
    }
    int subject_id? {
      description = "Novo ID da disciplina associada."
    }
    timestamp due_date? {
      description = "Nova data de prazo."
    }
    text status? {
      description = "Novo status da tarefa (ex: pending, in_progress, completed)."
    }
    text priority? {
      description = "Nova prioridade da tarefa (ex: low, medium, high)."
    }
  }

  stack {
    // 1. Lógica de Validação de Propriedade
    db.query "academic_tasks" {
      where = $db.academic_tasks.id == $input.academic_tasks_id,
      return = {
        type: "firstOrFail"
      }
    } as $task

    precondition ($task.user_id == $auth.id) {
      error_type = "accessdenied",
      error = "Você não tem permissão para editar este recurso."
    }

    // 2. Atualizar o registro no banco de dados
    db.update "academic_tasks" {
      id = $input.academic_tasks_id,
      data = $input
    } as $updated_task
  }

  response = $updated_task
}