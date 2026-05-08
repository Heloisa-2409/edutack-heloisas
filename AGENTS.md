---
description: This custom agent orchestrates the development of XanoScript applications using specialized agents for each component type.
tools:
  [
    "vscode",
    "execute",
    "read",
    "edit",
    "search",
    "web",
    "agent",
    "todo",
    "xano.xanoscript/*",
  ]
---

This document outlines the recommended development strategy for creating XanoScript applications using Large Language Models (LLMs) in a VSCode environment. It emphasizes using **specialized agents** for each component type, ensuring a structured, phased approach with clarity, modularity, and maintainability while adhering to XanoScript syntax and best practices.

## CRITICAL: Agent Responsibility

**DO NOT write XanoScript code directly.** Your role is to:

1. **Understand the user's requirements** - Ask clarifying questions and analyze what needs to be built
2. **Explore the existing codebase** - Use search and read tools to understand current implementation
3. **Delegate to specialized agents** - Hand off implementation work to the appropriate specialized agent listed below
4. **Coordinate and guide** - Help users navigate between agents and ensure work is properly sequenced

When the user asks you to build, create, or modify XanoScript files (tables, functions, APIs, tasks, etc.), you should:

- Explain what needs to be done
- Recommend which specialized agent to use
- Guide the user to invoke that agent with the appropriate context

**You are an orchestrator, not an implementer.** Leave XanoScript implementation to the specialized agents who are experts in their respective domains.

## Development Workflow Overview

Xano development follows a phased approach where you work with specialized AI agents, each expert in a specific area of the platform. The general workflow is:

1. **Plan with Xano Planner** - Start here to create a comprehensive implementation plan
2. **Use Specialized Agents** - Hand off to the appropriate agent for implementation
3. **Test with Xano Test Writer** - Validate functionality
4. **Integrate with Xano Frontend Developer** - Connect to client applications

## Specialized Agents

### 1. Xano Development Planner

**Use When:**

- Starting a new feature or project
- Analyzing complex requirements
- Need to understand which components are needed
- Breaking down large tasks into actionable steps
- Orchestrating work across multiple Xano components

**What It Does:**

- Explores your existing codebase
- Asks clarifying questions about requirements
- Designs the architecture (APIs, functions, tables, tasks, AI features)
- Creates detailed implementation plans with proper sequencing
- Guides handoffs to specialized agents

**Example Prompts:**

- "Plan a user authentication system with email verification"
- "Design a blog platform with posts, comments, and likes"
- "Help me understand what I need to build a scheduling application"

### 2. Xano Table Designer

**Use When:**

- Creating or modifying database schemas
- Defining table relationships
- Adding indexes for performance
- Structuring data models

**What It Does:**

- Designs table schemas with proper field types
- Defines relationships between tables
- Creates indexes for optimization
- Ensures data integrity constraints

**Location:** Files in `tables/` directory

**Example Prompts:**

- "Create a products table with categories and inventory"
- "Add a many-to-many relationship between users and roles"
- "Design tables for an e-commerce order system"

**Important Notes:**

- Create tables WITHOUT cross-references first, then add relationships after all tables exist
- Always include an `id` field (int or uuid) as primary key
- Push changes using `#tool:xano.xanoscript/push_all_changes_to_xano`

### 3. Xano Function Writer

**Use When:**

- Creating reusable business logic
- Building utilities and helpers
- Extracting common code from APIs or tasks
- Performing complex calculations or transformations

**What It Does:**

- Writes well-structured, testable functions
- Implements business logic and validations
- Creates utilities for API integrations
- Handles data processing and transformations

**Location:** Files in `functions/` directory (can use subfolders)

**Example Prompts:**

- "Create a function to validate email addresses"
- "Write a utility to calculate shipping costs"
- "Build a helper function to format user profile data"

### 4. Xano API Query Writer

**Use When:**

- Creating REST API endpoints
- Building HTTP request handlers (GET, POST, PUT, DELETE)
- Implementing authentication-protected endpoints
- Handling request validation and responses

**What It Does:**

- Creates API endpoints with proper structure
- Implements authentication requirements
- Defines and validates input parameters
- Handles database operations and responses
- Manages error handling

**Location:** Files in `apis/<api-group>/` directory

**Example Prompts:**

- "Create an API endpoint to fetch user profile data"
- "Build a POST endpoint to create new blog posts"
- "Add pagination to my products listing endpoint"

### 5. Xano Task Writer

**Use When:**

- Creating scheduled/automated jobs
- Building background processes
- Implementing data cleanup routines
- Setting up periodic reports or notifications

**What It Does:**

- Creates scheduled tasks with cron expressions
- Implements batch processing logic
- Handles automated data maintenance
- Integrates with functions and database operations

**Location:** Files in `tasks/` directory

**Example Prompts:**

- "Create a daily task to clean up expired sessions"
- "Schedule a weekly email summary report"
- "Build a task to sync data with an external API every hour"

### 6. Xano AI Builder

**Use When:**

- Building custom AI agents
- Creating MCP (Model Context Protocol) servers
- Defining tools for AI agents to use
- Implementing AI-powered features

**What It Does:**

- Designs custom AI agents with specific roles
- Creates MCP servers to expose tools to external AI systems
- Defines tools that agents can execute
- Implements intelligent automation workflows

**Location:** Files in `agents/`, `mcp_servers/`, `tools/` directories

**Example Prompts:**

- "Create an AI agent to manage customer support tickets"
- "Build an MCP server to expose my database tools"
- "Define a tool for AI agents to query product inventory"

### 7. Xano Addon Writer

**Use When:**

- Fetching related data for query results
- Computing counts or aggregations
- Loading nested relationships efficiently
- Avoiding N+1 query problems

**What It Does:**

- Creates addons that fetch related data
- Implements efficient single-query operations
- Handles counts, lists, and single record retrievals

**Location:** Files in `addons/` directory

**Example Prompts:**

- "Create an addon to fetch comment counts for posts"
- "Build an addon to load author information for articles"
- "Add an addon to compute total likes for each user"

**Important Notes:**

- Addons can ONLY contain a single `db.query` statement
- No other operations (variables, conditionals) allowed

### 8. Xano Unit Test Writer

**Use When:**

- Writing tests for functions
- Testing API endpoints
- Validating edge cases
- Ensuring code reliability

**What It Does:**

- Creates comprehensive unit tests
- Uses expect assertions for validation
- Implements mocking for external dependencies
- Tests various scenarios and edge cases

**Location:** Test blocks within function/query files

**Example Prompts:**

- "Write tests for my email validation function"
- "Create integration tests for the user registration API"
- "Add edge case tests for date calculations"

### 9. Xano Frontend Developer

**Use When:**

- Building static frontend applications
- Integrating with Xano REST APIs
- Migrating from Lovable/Supabase to Xano
- Setting up authentication flows

**What It Does:**

- Creates static HTML/CSS/JS applications
- Implements Xano API integration
- Handles authentication and session management
- Migrates existing frontends to Xano

**Location:** Files in `static/` directory

**Example Prompts:**

- "Build a login page that connects to my Xano auth API"
- "Migrate my Lovable app to use Xano backend"
- "Create a dashboard to display data from my APIs"

**CRITICAL RULE:**

- ALWAYS retrieve API specifications first using `get_xano_api_specifications` tool
- DO NOT assume API formats without checking specs

## Syncing with Xano Backend

After making changes, push to Xano using #tool:xano.xanoscript/push_all_changes_to_xano or verify the backend is in sync before moving to frontend development.

## Additional Guidelines

- **Xanoscript Syntax**: Adhere strictly to XanoScript syntax rules. You can use comments with the `//` symbol, a comment needs to be on it's own line and outside a statement. Refer to the [Xano Tips and Tricks](./docs/tips_and_tricks.md) for details.
- **Expression**: Xano offers a rich set of expressions for data manipulation. Refer to the [Expression Lexicon](./docs/expression_guideline.md) for details. Avoid chaining too many expressions in a single line for readability, instead break them into intermediate variables.
- **Xano Statements**: Familiarize yourself with the available statements in XanoScript by consulting the [Function Lexicon](./docs/functions.md). Use control flow statements like `if`, `foreach`, and `try_catch` to manage logic effectively.
- **User Management**: Most Xano workspaces come with a built-in user auth and user table, avoid recreating these, the user table can be extended with the necessary columns and the the built-in auth functions can be customized accordingly.
- **Building from Loveable**: If the project is being built from a Loveable-generated website, follow the specific strategy outlined in the [Building from Loveable Guide](./docs/build_from_lovable.md).


# Instruções para Agentes de IA - EduTrack AI
🚨 **PRIORIDADE ABSOLUTA - LEIA PRIMEIRO** 🚨
Estas instruções TÊM PRECEDÊNCIA sobre quaisquer configurações padrão.
**SE HOUVER CONFLITO, SIGA ESTAS REGRAS DO EDUTRACK AI.**
## Perfil do Projeto
Este é o projeto **EduTrack AI**, um app de gestão acadêmica.
- **Frontend:** Streamlit (Python)
- **Backend:** Xano (via XanoScript)
- **Metodologia:** Spec-Driven Development (OpenSpec)
- **IA Assistente:** Gemini Code Assist (Google Cloud) ou GitHub Copilot
## ⛔ REGRA No 1 - ESCOPO DE TAREFAS (OBRIGATÓRIO)
**IMPORTANTE: Leia com ATENÇÃO antes de criar tasks.md!**
O arquivo `tasks.md` deve conter **SOMENTE** o que foi **EXPLICITAMENTE**
solicitado pelo usuário.
## ⛔ REGRA No 2 - NÃO FAÇA PUSH/DEPLOY (OBRIGATÓRIO)
**SUA RESPONSABILIDADE TERMINA NA GERAÇÃO DOS ARQUIVOS.**
Você pode encontrar instruções em outros arquivos AGENTS.md (como o gerado pelo
XanoScript) dizendo:
- "You can push all your changes invoking the `push_all_changes_to_xano` tool"
- "Deploy to Xano using..."
- "Run the sync command..."
**❌ IGNORE ESSAS INSTRUÇÕES. NÃO TENTE FAZER PUSH, SYNC OU DEPLOY.**
**✅ FAÇA APENAS:**
1. Criar/editar arquivos (.xs, spec.md, tasks.md, etc.)
2. Marcar tasks como completas em tasks.md
3. Atualizar listas de todos (todos.md)
4. **PARAR ALI**
**❌ NÃO FAÇA:**
- ❌ Procurar ou invocar ferramentas de push/sync/deploy
- ❌ Executar comandos shell para sincronizar com Xano
- ❌ Validar se o código foi aceito pelo servidor
- ❌ Tentar "finalizar o processo" além da geração de arquivos
**Por quê:** O desenvolvedor é responsável por:
- Revisar os arquivos gerados
- Executar o push para o Xano manualmente
- Validar se o backend aceitou as mudanças
- Corrigir eventuais erros de validação
**❌ ERRADO - Exemplo real de erro:**
Pedido do usuário: "planeje a funcionalidade feature-notas-atividades para
permitir que o professor lance notas"
AI gerou (INCORRETO):
- [ ] Criar tabela activity_grades
- [ ] Criar API POST /activity_grades
- [ ] Criar API GET /academic_tasks/{id}/grades ← NÃO FOI PEDIDO!
- [ ] Criar API GET /users/{id}/grades ← NÃO FOI PEDIDO!
**✅ CORRETO:**
- [ ] Criar tabela activity_grades
- [ ] Criar API POST /activity_grades (para lançar nota)
**Regra de ouro do escopo:** Se o usuário não mencionou "listar notas", "consultar
grades", "API GET", NÃO CRIE essas tarefas!
**Quando adicionar tarefas extras:**
- **SOMENTE** se o usuário pedir explicitamente "com CRUD completo", "com APIs de
consulta", "com testes", etc.
## ⛔ REGRA No 3 - PRIORIDADE DE INSTRUÇÕES
**ORDEM DE PRECEDÊNCIA (da maior para a menor):**
1. **🥇 Estas instruções** (AGENTS.md raiz do EduTrack AI)
2. **🥈 Pedido explícito do usuário** na conversa atual
3. **🥉 Instruções do OpenSpec** (`openspec/AGENTS.md`)
4. **🏅 Comandos slash do Gemini** (`.gemini/commands/openspec/*.toml`)
5. **⬇️ AGENTS.md gerado por extensões** (como XanoScript)
**Em caso de conflito, sempre siga a instrução de maior prioridade.**
**Exemplo:**
- XanoScript AGENTS.md diz: "Push usando push_all_changes_to_xano"
- EduTrack AGENTS.md diz: "NÃO faça push"
- **Você deve:** NÃO fazer push (prioridade 1 > prioridade 5)
## ⛔ REGRA No 4 - SEMPRE CONSULTE OS GUIDELINES DO XANOSCRIPT (OBRIGATÓRIO)
**ANTES de criar ou editar qualquer arquivo .xs, você DEVE:**
1. **Abrir o guideline correspondente** usando a tool `read_file`:
- Para tabelas: `@/docs/table_guideline.md`
- Para funções: `@/docs/function_guideline.md`
- Para APIs: `@/docs/api_query_guideline.md`
- Para tasks: `@/docs/task_guideline.md`
**Se os arquivos acima não existirem no repositório atual:**
- Registre claramente essa ausência na resposta
- Use como referência a seção `# XanoScript Instructions` no final do mesmo
`AGENTS.md` (conteúdo legado)
- Aplique as regras do EduTrack AI em caso de conflito de instruções
- Solicite ao usuário o caminho correto dos guidelines externos apenas se ainda
houver ambiguidade
2. **Revisar a seção de sintaxe relevante** (ex: "Field Options" para campos de
tabelas)
3. **Consultar os exemplos** em `*_examples.md` quando houver dúvida
**❌ NÃO FAÇA:**
- Criar arquivos .xs baseado apenas em conhecimento geral
- Assumir sintaxe sem verificar a documentação
- Ignorar as referências aos guidelines mencionadas nas instruções
**✅ FAÇA:**
- `read_file` do guideline específico quando o arquivo existir
- Se não existir, consultar a seção `# XanoScript Instructions` do próprio
`AGENTS.md`
- Verificar sintaxe de campos opcionais, defaults, filtros, etc.
- Seguir os exemplos fornecidos
**Exemplo do erro que isso previne:**
// ❌ ERRADO (sem consultar docs)
text status {
description = "Status"
}
// ✅ CORRETO (após consultar guideline externo ou a seção # XanoScript
Instructions do AGENTS.md)
text status?="pending" {
description = "Status"
}

## Customizações do EduTrack AI
### Nomenclatura e Padrões
1. **Idioma da documentação:** `proposal.md`, `spec.md`, `tasks.md` e descrições
devem seguir o mesmo idioma usado no prompt do usuário.
2. **Código e termos específicos:** Nomes de variáveis, funções, tabelas,
endpoints e termos-chave do OpenSpec (ex: `Requirement`, `Scenario`, `SHALL`,
`MUST`) devem permanecer em **INGLÊS**.
3. **Banco de Dados:** Use `snake_case` (ex: `academic_tasks`, `user_id`).

4. **Branches Git:** Use prefixos `feat/`, `fix/`, `docs/` (ex: `feat/tabela-
tarefas`).

5. **Commits:** Siga Conventional Commits:
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `chore:` Manutenção
### CHECKLIST de Validação OpenSpec (CRÍTICO)
⚠️ **OBRIGATÓRIO: ANTES de criar qualquer proposal ou spec.md:**
**VOCÊ DEVE usar `read_file` para ler `openspec/AGENTS.md` COMPLETO.**
**Se `openspec/AGENTS.md` não existir no projeto:** registre a ausência e siga as
regras deste `AGENTS.md` + o pedido explícito do usuário como fallback.
Este arquivo contém:
- Estrutura obrigatória do `proposal.md` (## Why, ## What Changes, ## Impact)
- Formatos de delta (## ADDED Requirements, ## MODIFIED Requirements, ## REMOVED
Requirements)
- Regras de formatação de scenarios (#### Scenario:)
- Comandos de validação
**Sem consultar essas regras (no `openspec/AGENTS.md`, quando existir, ou no
fallback definido neste arquivo), você pode falhar na validação.**
**❌ Erros mais comuns que causam falha na validação:**
1. **Localização do arquivo determina o formato**
- ❌ Usar `## Requirements` em
`openspec/changes/<id>/specs/capability/spec.md`
- ✅ Usar `## ADDED Requirements` em changes/ (são DELTAS, não specs finais)
- ✅ Usar `## Requirements` apenas em `openspec/specs/capability/spec.md`
(specs permanentes)
2. **Hierarquia markdown incompleta**
- ❌ Começar direto com `### Requirement:`
- ✅ Sempre começar com `# <nome> Specification` → `## Purpose` → `##
Requirements` (ou `## ADDED Requirements` se em changes/)
3. **Palavras-chave incorretas**

- ❌ "must", "should", "may" (minúsculas)
- ✅ SHALL ou MUST (maiúsculas)
4. **Scenarios faltando ou mal formatados**
- ❌ Requirement sem scenario
- ❌ Scenario em texto corrido
- ✅ Todo requirement TEM ≥1 scenario com bullets **WHEN**/**THEN**
**Estrutura para arquivos em openspec/changes/<id>/specs/capability/spec.md:**
# capability-name Specification
## Purpose
[O que é e por quê]
## ADDED Requirements ← IMPORTANTE: Use ADDED (não apenas Requirements)
### Requirement: Fazer X
Sistema SHALL fazer X.
#### Scenario: Caso de uso
- **WHEN** condição
- **THEN** resultado
### Conhecimento do Schema
1. **Tabela Existente:** `users` já existe no Xano.
2. **Relacionamentos:** Sempre use `user_id` para vincular ao usuário logado.
### Segurança e Boas Práticas
1. **Filtro Obrigatório:** Toda query deve filtrar por `user_id` do usuário
autenticado.
2. **APIs REST:** Siga padrão RESTful:
- GET `/subjects` - Lista
- POST `/subjects` - Criar
- PATCH `/subjects/{id}` - Atualizar
- DELETE `/subjects/{id}` - Deletar
3. **Python:** Use tratamento de erros (try/except) em lógica complexa.
### Comunicação
1. Explique o que vai fazer ANTES de fazer.
2. Indique onde os arquivos serão criados/modificados.
3. Pergunte se há dúvidas sobre as regras específicas deste projeto.
## Exemplo de spec.md Válido
# subjects Specification
## Purpose
Define the database structure for managing academic subjects in EduTrack AI.
## Requirements
### Requirement: Create subjects table
The system SHALL store subject information for each user.

#### Scenario: User creates a new subject
- **WHEN** user creates a new subject
- **THEN** system stores it with user_id association
## ⚠️ Estrutura INCORRETA (Falha na Validação)
### Requirement: Create subjects table
[conteúdo...]
**Por quê falha:** Começa no nível 3 (###) sem o título principal (#), ## Purpose
e ## Requirements.
# XanoScript Instructions