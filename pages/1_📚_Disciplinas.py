import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Xano
XANO_WORKSPACE_URL = os.getenv('XANO_WORKSPACE_URL', 'https://x8ki-letl-twmt.xano.io/api')

# Função helper para API
def make_xano_request(endpoint, method='GET', data=None, headers=None):
    """Faz uma requisição para a API Xano com tratamento de erro aprimorado."""
    url = f"{XANO_WORKSPACE_URL}{endpoint}"
    default_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {st.session_state.get("auth_token", "")}'
    }
    if headers:
        default_headers.update(headers)

    try:
        if method == 'GET':
            response = requests.get(url, headers=default_headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=default_headers)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, headers=default_headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=default_headers)
        else:
            st.error(f"Método HTTP desconhecido: {method}")
            return None

        # Lança uma exceção para códigos de erro (4xx ou 5xx)
        response.raise_for_status()

        # Para respostas bem-sucedidas que não têm conteúdo (ex: DELETE)
        if response.status_code == 204:
            return {"status": "success"}
        
        return response.json()

    except requests.exceptions.HTTPError as err:
        try:
            error_details = err.response.json()
            st.error(f"Erro da API: {error_details.get('message', 'Resposta de erro sem mensagem.')}")
        except ValueError:
            st.error(f"Erro na API (código {err.response.status_code}). A resposta não pôde ser decodificada.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: {e}")
        return None

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
                    st.error("Erro ao cadastrar disciplina. Verifique os dados e tente novamente.")
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
                                else:
                                    st.error("Falha ao atualizar a disciplina.")

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
    else:
        st.error("Erro ao carregar disciplinas. Verifique sua conexão.")