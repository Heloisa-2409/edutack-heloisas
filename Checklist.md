🔐 Autenticação e Acesso
++ Permitir que o usuário crie uma conta com e-mail e senha.
++ Permitir que o usuário faça login e acesse o sistema com suas credenciais.
++ Manter o usuário autenticado durante a navegação entre páginas.
++ Permitir que o usuário visualize e edite seu perfil (nome, e-mail).
++ Permitir que o usuário redefina sua senha via e-mail.
++ Encerrar a sessão automaticamente quando o token de autenticação expirar.

📚 Gestão de Disciplinas
++ Permitir que o usuário cadastre uma disciplina informando nome, professor e carga horária.
++ Garantir que as disciplinas cadastradas sejam armazenadas no banco de dados e vinculadas ao usuário logado.
++ Listar todas as disciplinas do usuário.
++ Permitir que o usuário edite os dados de uma disciplina.
++ Permitir que o usuário exclua uma disciplina.
++ Impedir o cadastro de disciplinas duplicadas (mesmo nome e professor).
++ Permitir buscar disciplinas por nome.
++ Permitir filtrar disciplinas que possuem tarefas em atraso.

📝 Gestão de Tarefas
++ Permitir que o usuário cadastre uma tarefa vinculada a uma disciplina, informando título, descrição e prazo.
++ Garantir que as tarefas cadastradas sejam armazenadas no banco de dados e associadas à disciplina e ao usuário corretos.
++ Listar todas as tarefas do usuário, agrupadas por disciplina ou por prazo.
++ Permitir que o usuário edite os dados de uma tarefa.
++ Permitir que o usuário exclua uma tarefa. (Bug do st.confirm corrigido)
++ Permitir que o usuário marque uma tarefa como concluída.
++ Permitir filtrar tarefas por status (Pendente, Em andamento, Concluída).
++ Identificar e sinalizar visualmente as tarefas com prazo vencido.

🏠 Propostas de Melhoria
Dashboard
++ Criar uma tela inicial com visão geral do sistema logo após o login, exibindo:
++ Total de disciplinas ativas
++ Total de tarefas pendentes e em atraso
++ As próximas tarefas com prazo mais próximo
++ Indicador de progresso geral (percentual de tarefas concluídas)

Relatórios e Progresso
-- Criar uma tela de relatórios com o histórico de tarefas por período e progresso por disciplina.
-- Permitir que o usuário exporte seus dados (disciplinas e tarefas) em formato CSV ou PDF.

Evolução das Disciplinas e Tarefas
-- Permitir associar um semestre/período a cada disciplina para melhor organização.
-- Adicionar campo de prioridade nas tarefas (Baixa, Média, Alta).
-- Exibir o progresso de cada disciplina com base nas tarefas concluídas.
-- Permitir arquivar disciplinas concluídas sem excluí-las.

Design e Experiência do Usuário
++ Definir uma identidade visual consistente para o app (cores, logo, tipografia).
++ Melhorar a tela de login e cadastro com um layout mais atrativo.
++ Exibir uma tela de boas-vindas para usuários que ainda não possuem dados cadastrados.
++ Solicitar confirmação antes de excluir disciplinas ou tarefas.