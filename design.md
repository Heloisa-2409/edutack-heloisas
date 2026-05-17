# subjects-crud Design

## 1. Visão Geral da Arquitetura

Esta funcionalidade será implementada inteiramente no backend Xano, modificando e/ou criando os seguintes arquivos XanoScript na pasta `apis/subjects/`.

- `subjects_GET.xs`: Listar todas as disciplinas do usuário.
- `subjects_POST.xs`: Criar uma nova disciplina.
- `subjects_{subjects_id}_GET.xs`: Obter uma disciplina específica.
- `subjects_{subjects_id}_PATCH.xs`: Atualizar uma disciplina específica.
- `subjects_{subjects_id}_DELETE.xs`: Deletar uma disciplina específica.

Todos os endpoints exigirão autenticação de usuário (`auth = "user"`).

## 2. Design Detalhado dos Endpoints

### `GET /subjects`

- **Arquivo:** `apis/subjects/subjects_GET.xs`
- **Autenticação:** `auth = "user"`
- **Lógica:**
    1. Usar a função `db.query` na tabela `subjects`.
    2. Aplicar um filtro `where` para retornar apenas os registros que satisfaçam **AMBAS** as condições:
        - `subjects.user_id == $auth.id`
        - `subjects.account_id == $auth.account_id`
    3. Retornar a lista de registros encontrados.

### `POST /subjects`

- **Arquivo:** `apis/subjects/subjects_POST.xs`
- **Autenticação:** `auth = "user"`
- **Inputs:** `name`, `professor`, `day_of_week` (e outros campos da tabela `subjects` que não sejam auto-gerados).
- **Lógica:**
    1. Receber os dados da nova disciplina no corpo da requisição.
    2. Antes de inserir, adicionar os seguintes campos ao objeto de entrada:
        - `user_id = $auth.id`
        - `account_id = $auth.account_id`
    3. Usar a função `db.insert` para adicionar o novo registro na tabela `subjects`.
    4. Retornar o registro completo que foi criado.

### Endpoints por ID (`/subjects/{subjects_id}`)

Para os endpoints `GET`, `PATCH`, e `DELETE` que operam em um registro específico, a lógica de validação de propriedade é crucial e deve ser executada primeiro.

#### Lógica de Validação de Propriedade (Precondition)

1. **Receber `subjects_id`** da URL.
2. **Buscar o registro:**
   - Usar `db.query` na tabela `subjects`.
   - Aplicar um filtro `where subjects.id == {subjects_id}`.
   - Usar a opção `firstOrFail` para garantir que o registro exista. Se não existir, a API deve retornar um erro `notfound`.
3. **Verificar a Propriedade:**
   - Após encontrar o registro, verificar se `record.user_id == $auth.id` E `record.account_id == $auth.account_id`.
   - Se a verificação falhar, a API deve parar a execução e retornar um erro `accessdenied`.
   - **NÃO** prossiga com a operação (leitura, atualização ou exclusão) se a propriedade não for confirmada.

### `GET /subjects/{subjects_id}`

- **Arquivo:** `apis/subjects/subjects_{subjects_id}_GET.xs`
- **Autenticação:** `auth = "user"`
- **Lógica:**
    1. Executar a **Lógica de Validação de Propriedade** descrita acima.
    2. Se a validação for bem-sucedida, retornar o registro encontrado.

### `PATCH /subjects/{subjects_id}`

- **Arquivo:** `apis/subjects/subjects_{subjects_id}_PATCH.xs`
- **Autenticação:** `auth = "user"`
- **Inputs:** Campos a serem atualizados.
- **Lógica:**
    1. Executar a **Lógica de Validação de Propriedade**.
    2. Se a validação for bem-sucedida, usar `db.update` para aplicar as alterações no registro correspondente ao `subjects_id`.
    3. Retornar o registro atualizado.

### `DELETE /subjects/{subjects_id}`

- **Arquivo:** `apis/subjects/subjects_{subjects_id}_DELETE.xs`
- **Autenticação:** `auth = "user"`
- **Lógica:**
    1. Executar a **Lógica de Validação de Propriedade**.
    2. Se a validação for bem-sucedida, usar `db.delete` para remover o registro correspondente ao `subjects_id`.
    3. Retornar uma confirmação de sucesso (ex: o registro deletado ou uma mensagem).

## 3. Tratamento de Erros

- **`notfound`**: Retornar quando um `subjects_id` é fornecido, mas nenhum registro com esse ID existe na tabela. Isso é tratado nativamente com `firstOrFail`.
- **`accessdenied`**: Retornar quando um registro com o `subjects_id` fornecido existe, mas não pertence ao usuário autenticado (`user_id` ou `account_id` não correspondem). Isso deve ser implementado com uma verificação condicional (`if`).