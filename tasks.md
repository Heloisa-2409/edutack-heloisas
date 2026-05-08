# feature-notas-atividades — Plano de Implementação

## 📋 Resumo
Funcionalidade para permitir que professores lancem notas para alunos em atividades específicas.

**Escopo:** APENAS o que foi solicitado:
- ✅ Criar tabela `activity_grades`
- ✅ Criar API POST para lançar nota

**Excluídos (não solicitados):**
- ❌ APIs de listagem/consulta (GET, PATCH, DELETE)
- ❌ Funções reutilizáveis
- ❌ UI Streamlit

---

## 📌 Tarefas

### 1. Tabela `activity_grades`
- [ ] Usar **Xano Table Designer** para criar tabela em `tables/activity_grades.xs`
- [ ] Campos obrigatórios: `id`, `created_at`, `updated_at`, `user_id`, `account_id`, `student_id`, `activity_name`, `grade`
- [ ] Campos opcionais: `subject_id`, `activity_id`, `comments`
- [ ] Validação: `grade` deve aceitar valores numéricos (0-100)
- [ ] Relacionamento: `subject_id` referencia tabela `subjects` (opcional)

### 2. API POST `/activity_grades`
- [ ] Usar **Xano API Query Writer** para criar em `apis/activity_grades/`
- [ ] Autenticação: `auth = "user"`
- [ ] Input: `student_id`, `activity_name`, `grade`, `subject_id?`, `activity_id?`, `comments?`
- [ ] Ação: Inserir registro com `user_id = $auth.id` e `account_id = $auth.account_id`
- [ ] Resposta: Retornar registro criado

---

## 🔄 Sequência de Implementação

1. **Primeiro:** Criar tabela `activity_grades` (dependência para API)
2. **Depois:** Criar API `POST /activity_grades`
3. **Verificação:** Confirmar que ambos os componentes sincronizam com Xano manualmente

---

## ✅ Definição de Pronto

- [ ] Tabela criada com sucesso em Xano
- [ ] API aceita requisições POST com os inputs corretos
- [ ] Registro é inserido com `user_id` do professor autenticado
- [ ] Registros são isolados por `account_id` (multi-tenant)
- [ ] Proposta validada contra regras OpenSpec (estrutura: ## Why, ## What Changes, ## Impact)
