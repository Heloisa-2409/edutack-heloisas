import streamlit as st
from datetime import datetime
from utils.api import make_xano_request

st.title("📝 Gerenciamento de Tarefas")

# Buscar disciplinas para o select
subjects = make_xano_request('/subjects')
subjects_options = {subject['name']: subject['id'] for subject in subjects} if subjects else {}

# Abas para funcionalidades
tab_lista, tab_novo = st.tabs(["📋 Minhas Tarefas", "➕ Nova Tarefa"])

with tab_novo:
    st.subheader("Criar Nova Tarefa")

    with st.form("form_tarefa"):
        title = st.text_input("Título da Tarefa", placeholder="Ex: Estudar capítulo 5")
        description = st.text_area("Descrição", placeholder="Detalhes da tarefa...")
        subject_name = st.selectbox("Disciplina", options=list(subjects_options.keys()) if subjects_options else ["Nenhuma disciplina cadastrada"])
        due_date = st.date_input("Prazo de Entrega", min_value=datetime.today().date())
        status = st.selectbox("Status", ["pending", "in_progress", "completed"])

        submitted = st.form_submit_button("Criar Tarefa")

        if submitted:
            if title and subject_name != "Nenhuma disciplina cadastrada":
                # Criar tarefa via API
                task_data = {
                    "title": title,
                    "description": description,
                    "subject_id": subjects_options[subject_name],
                    "due_date": due_date.isoformat(),
                    "status": status
                }

                result = make_xano_request('/academic_tasks', method='POST', data=task_data)

                if result:
                    st.success(f"Tarefa '{title}' criada com sucesso!")
                    st.rerun()
            else:
                st.error("Preencha o título e selecione uma disciplina.")

with tab_lista:
    st.subheader("Minhas Tarefas")

    # Filtros
    col1, col2 = st.columns([3, 1])

    with col1:
        search = st.text_input("Buscar tarefa...", placeholder="Digite para filtrar...")

    with col2:
        status_filter = st.selectbox("Status", ["Todas", "pending", "in_progress", "completed"])

    # Buscar tarefas via API
    tasks = make_xano_request('/academic_tasks')

    if tasks:
        # Aplicar filtros
        filtered_tasks = tasks

        if search:
            filtered_tasks = [t for t in filtered_tasks if search.lower() in t.get('title', '').lower() or search.lower() in t.get('description', '').lower()]

        if status_filter != "Todas":
            filtered_tasks = [t for t in filtered_tasks if t.get('status') == status_filter]

        if len(filtered_tasks) > 0:
            # Exibir tarefas
            for task in filtered_tasks:
                # Encontrar nome da disciplina
                subject_name = "Desconhecida"
                if subjects:
                    for subject in subjects:
                        if subject['id'] == task.get('subject_id'):
                            subject_name = subject['name']
                            break

                # Calcular dias restantes
                due_date = datetime.fromisoformat(task.get('due_date', '').split('T')[0]) if task.get('due_date') else None
                days_left = (due_date - datetime.now()).days if due_date else None

                # Cor baseada no status
                status_colors = {
                    "pending": "🟡",
                    "in_progress": "🟠",
                    "completed": "🟢"
                }

                with st.expander(f"{status_colors.get(task.get('status'), '⚪')} {task.get('title', 'Sem título')}", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.write(f"**Disciplina:** {subject_name}")
                        st.write(f"**Prazo:** {due_date.strftime('%d/%m/%Y') if due_date else 'Não definido'}")
                        if days_left is not None:
                            if days_left < 0:
                                st.error(f"⚠️ Atrasada há {abs(days_left)} dias")
                            elif days_left == 0:
                                st.warning("📅 Vence hoje!")
                            else:
                                st.info(f"⏰ Faltam {days_left} dias")

                    with col2:
                        st.write(f"**Status:** {task.get('status', 'pending').replace('_', ' ').title()}")

                    with col3:
                        # Botões de ação
                        if st.button("✅ Concluir", key=f"complete_{task['id']}", disabled=task.get('status') == 'completed'):
                            make_xano_request(f'/academic_tasks/{task["id"]}', method='PATCH', data={"status": "completed"})
                            st.rerun()

                        if st.button("🗑️ Excluir", key=f"delete_{task['id']}"):
                            if st.confirm("Tem certeza que deseja excluir esta tarefa?"):
                                make_xano_request(f'/academic_tasks/{task["id"]}', method='DELETE')
                                st.rerun()

                    if task.get('description'):
                        st.write(f"**Descrição:** {task['description']}")

            # Estatísticas
            total_tasks = len(filtered_tasks)
            completed_tasks = len([t for t in filtered_tasks if t.get('status') == 'completed'])
            pending_tasks = len([t for t in filtered_tasks if t.get('status') == 'pending'])

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Tarefas", total_tasks)
            col2.metric("Concluídas", completed_tasks)
            col3.metric("Pendentes", pending_tasks)
        else:
            st.info("Nenhuma tarefa encontrada com os filtros aplicados.")