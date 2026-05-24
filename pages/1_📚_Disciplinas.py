import streamlit as st
from utils.api import make_xano_request

st.set_page_config(page_title="Disciplinas", page_icon="📚")
st.title("Gestão de Disciplinas")

# Abas para separar Listagem de Cadastro
tab_lista, tab_novo = st.tabs(["📋 Listar", "➕ Nova Disciplina"])

with tab_novo:
    st.subheader("Cadastrar Nova Matéria")

    with st.form("form_disciplina"):
        nome = st.text_input("Nome da Disciplina", placeholder="Ex: Matemática")
        professor = st.text_input("Nome do Professor", placeholder="Ex: Prof. Silva")
        dia_semana = st.selectbox("Dia da Aula", ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"])
        submitted = st.form_submit_button("Salvar")

        if submitted:
            if nome and professor:
                # Criar disciplina via API
                disciplina_data = {
                    "name": nome,
                    "professor": professor,
                    "day_of_week": dia_semana
                }

                result = make_xano_request('/subjects', method='POST', data=disciplina_data)

                if result:
                    st.success(f"Disciplina '{nome}' cadastrada com sucesso!")
                    st.rerun()  # Recarregar a página para mostrar na lista
            else:
                st.error("Preencha todos os campos obrigatórios.")

with tab_lista:
    st.subheader("Suas Disciplinas")

    # Buscar disciplinas via API
    subjects = make_xano_request('/subjects')

    if subjects:
        if len(subjects) > 0:
            st.write(f"Você tem **{len(subjects)}** disciplina(s) cadastrada(s).")

            # Cabeçalho da lista
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            col1.markdown("**Nome**")
            col2.markdown("**Professor**")
            col3.markdown("**Dia**")
            col4.markdown("**Ações**")

            st.markdown("---")

            # Listar cada disciplina
            for subject in subjects:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                col1.write(subject.get("name", "N/A"))
                col2.write(subject.get("professor", "N/A"))
                col3.write(subject.get("day_of_week", "N/A"))
                
                action_col1, action_col2 = col4.columns(2)

                # Botão de Edição
                if action_col1.button("✏️", key=f"edit_{subject.get('id')}", help="Editar disciplina"):
                    with st.dialog("Editar Disciplina", width="large"):
                        with st.form(key=f"edit_form_{subject.get('id')}"):
                            st.subheader(f"Editando: {subject.get('name')}")

                            # Campos do formulário pré-preenchidos
                            new_name = st.text_input("Nome da Disciplina", value=subject.get("name"))
                            new_professor = st.text_input("Nome do Professor", value=subject.get("professor"))
                            
                            dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
                            try:
                                current_day_index = dias.index(subject.get("day_of_week"))
                            except ValueError:
                                current_day_index = 0

                            new_day_of_week = st.selectbox("Dia da Aula", dias, index=current_day_index)

                            if st.form_submit_button("Salvar Alterações"):
                                update_data = {"name": new_name, "professor": new_professor, "day_of_week": new_day_of_week}
                                result = make_xano_request(f"/subjects/{subject.get('id')}", method='PATCH', data=update_data)
                                if result:
                                    st.toast(f"Disciplina '{new_name}' atualizada com sucesso!")
                                    st.rerun()

                # Botão de Arquivar
                if action_col2.button("🗑️", key=f"archive_{subject.get('id')}", help="Arquivar disciplina"):
                    with st.dialog("Confirmar Arquivamento"):
                        st.warning(f"Tem certeza que deseja arquivar a disciplina **{subject.get('name')}**?")
                        st.write("Esta ação não pode ser desfeita.")
                        
                        col_confirm, col_cancel = st.columns(2)
                        
                        if col_confirm.button("Arquivar", key=f"confirm_archive_{subject.get('id')}"):
                            make_xano_request(f"/subjects/{subject.get('id')}", method='DELETE')
                            st.toast(f"Disciplina '{subject.get('name')}' arquivada com sucesso!")
                            st.rerun()
                        if col_cancel.button("Cancelar", key=f"cancel_archive_{subject.get('id')}"):
                            st.rerun()
        else:
            st.info("Nenhuma disciplina cadastrada ainda. Use a aba 'Nova Disciplina' para adicionar.")