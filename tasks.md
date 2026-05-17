# subjects-crud — Plano de Implementação

## 📋 Resumo
Criar e validar endpoints CRUD para a tabela `subjects`, garantindo que cada usuário só acesse os seus próprios registros.

**Escopo:**
- ✅ Revisar ou criar os endpoints RESTful para `subjects`
- ✅ Garantir autorização por `user_id` e `account_id`
- ✅ Manter apenas dados do usuário autenticado

---

## 📌 Tarefas

### 1. Revisar endpoints `subjects`
- [x] Verificar `apis/subjects/subjects_GET.xs` e `apis/subjects/subjects_POST.xs`
- [x] Verificar `apis/subjects/subjects_{subjects_id}_GET.xs`, `apis/subjects/subjects_{subjects_id}_PATCH.xs`, e `apis/subjects/subjects_{subjects_id}_DELETE.xs`
- [x] Assegurar que `auth = "user"` está habilitado em todos os endpoints

### 2. Garantir isolamento por usuário e tenant
- [x] Confirmar que o `GET /subjects` filtra por `user_id == $auth.id` e `account_id == $auth.account_id`
- [x] Confirmar que `POST /subjects` grava `user_id = $auth.id` e `account_id = $auth.account_id`
- [x] Confirmar que os endpoints por ID (`GET`, `PATCH`, `DELETE`) validam tanto a existência do registro quanto a propriedade (`user_id` e `account_id`) antes de qualquer operação.

### 3. Ajustes e correções
- [x] Corrigir qualquer endpoint que não faça validação de ownership.
- [x] Incluir mensagens de erro claras para `notfound` (registro não existe) e `accessdenied` (registro existe, mas pertence a outro usuário).

---

## ✅ Definição de Pronto

- [x] CRUD completo para `subjects` disponível.
- [x] Usuário autenticado só acessa seus próprios subjects.
- [x] `account_id` protege o isolamento multi-tenant.
- [x] Erros retornam `notfound` ou `accessdenied` conforme apropriado.