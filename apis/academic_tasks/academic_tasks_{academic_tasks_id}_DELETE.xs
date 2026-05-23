query "academic_tasks/{academic_tasks_id}" verb=DELETE {
  api_group = "academic_tasks"
  description = "Exclui uma tarefa acadêmica específica do usuário autenticado."
  auth = "user"

  input {
    int academic_tasks_id {
      description = "ID da tarefa acadêmica a ser excluída."
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
      error = "Você não tem permissão para excluir este recurso."
    }

    // 2. Excluir o registro do banco de dados
    db.delete "academic_tasks" {
      id = $input.academic_tasks_id
    } as $deleted_task
  }

  response = $deleted_task
}