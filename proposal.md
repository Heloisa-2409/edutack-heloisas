# Proposta feature-subjects-crud

## Por quê (Why)
- O backend do EduTrack AI precisa de uma API CRUD segura para `subjects` que mantenha os dados de cada usuário isolados.
- Esta funcionalidade DEVE impedir que usuários leiam, atualizem ou excluam `subjects` que não lhes pertencem.
- O design DEVE preservar o isolamento de tenants (multi-tenant) ao impor verificações de propriedade tanto por `user_id` quanto por `account_id`.

## O que muda (What Changes)
- Adicionar ou verificar os endpoints RESTful para o recurso `subjects`:
  - `GET /subjects`
  - `POST /subjects`
  - `GET /subjects/{subjects_id}`
  - `PATCH /subjects/{subjects_id}`
  - `DELETE /subjects/{subjects_id}`
- Garantir que cada endpoint use `auth = "user"`.
- Implementar a imposição de propriedade em cada operação:
  - `GET /subjects` DEVE filtrar por `$auth.id` e `$auth.account_id`.
  - `POST /subjects` DEVE criar registros com `user_id = $auth.id` e `account_id = $auth.account_id`.
  - Os endpoints `{subjects_id}` DEVEM verificar se o registro existe e pertence ao usuário autenticado antes de retorná-lo, atualizá-lo ou excluí-lo.
- Retornar tipos de erro claros para registros não autorizados ou ausentes:
  - `notfound` quando o registro não existe.
  - `accessdenied` quando o registro existe, mas pertence a outro usuário ou conta.

## Impacto (Impact)
- Fornece uma interface CRUD completa e com escopo definido para o gerenciamento de disciplinas.
- Protege os dados do usuário por meio de verificações de propriedade multi-tenant.
- Permite que os fluxos de trabalho do frontend listem, criem, atualizem e removam disciplinas com segurança.
- Mantém a implementação estritamente no escopo da funcionalidade solicitada, sem adicionar endpoints não relacionados ou padrões de acesso mais amplos.