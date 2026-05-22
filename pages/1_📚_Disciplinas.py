import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Xano
XANO_WORKSPACE_URL = os.getenv('XANO_WORKSPACE_URL', 'https://x8ki-letl-twmt.xano.io/api')

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="Disciplinas - EduTrack AI", page_icon="📚", layout="wide")

# ── Auth Guard ──────────────────────────────────────────────────────────────
if 'auth_token' not in st.session_state or not st.session_state.get('auth_token'):
    st.warning("⚠️ Você precisa fazer o login para acessar esta página.")
    st.page_link("pages/0_🔐_Login.py", label="Ir para Login", icon="🔐")
    st.stop()

# ── Estilo Premium ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@700&display=swap');

.main { font-family: 'Inter', sans-serif; }
.page-header {
    font-family: 'Outfit', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #1E3A8A;
    margin-bottom: 0.25rem;
}
.page-sub {
    color: #6B7280;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
    border-left: 4px solid #3B82F6;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.subject-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: box-shadow 0.2s;
}
.subject-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
}
.badge-blue { background: #DBEAFE; color: #1D4ED8; }
.badge-red  { background: #FEE2E2; color: #DC2626; }
.badge-green{ background: #D1FAE5; color: #065F46; }
.divider { border: none; border-top: 1px solid #F3F4F6; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Função helper para API ──────────────────────────────────────────────────
def make_xano_request(endpoint, method='GET', data=None):
    """Faz uma requisição para a API Xano com tratamento de 401 automático."""
    url = f"{XANO_WORKSPACE_URL}{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {st.session_state.get("auth_token", "")}'
    }
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return None

        if response.status_code == 401:
            st.session_state.pop('auth_token', None)
            st.error("⏱️ Sessão expirada. Por favor, faça login novamente.")
            st.rerun()

        response.raise_for_status()

        if response.status_code == 204:
            return {"status": "success"}
        return response.json()

    except requests.exceptions.HTTPError as err:
        try:
            error_details = err.response.json()
            st.error(f"❌ Erro da API: {error_details.get('message', 'Erro desconhecido.')}")
        except ValueError:
            st.error(f"❌ Erro na API (código {err.response.status_code}).")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro de conexão: {e}")
        return None

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-header">📚 Gestão de Disciplinas</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Gerencie suas matérias, professores e carga horária</p>', unsafe_allow_html=True)

# ── Abas ────────────────────────────────────────────────────────────────────
tab_lista, tab_novo = st.tabs(["📋 Minhas Disciplinas", "➕ Nova Disciplina"])

# ══════════════════════════════════════════════════════════════════════════════
# ABA: NOVA DISCIPLINA
# ══════════════════════════════════════════════════════════════════════════════
with tab_novo:
    st.subheader("Cadastrar Nova Matéria")

    with st.form("form_disciplina", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            nome = st.text_input("Nome da Disciplina *", placeholder="Ex: Cálculo I")
            professor = st.text_input("Nome do Professor *", placeholder="Ex: Prof. Silva")
        with col_b:
            dia_semana = st.selectbox("Dia da Aula", ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"])
            carga_horaria = st.number_input(
                "Carga Horária (h/semana)",
                min_value=0,
                max_value=20,
                value=2,
                step=1,
                help="Horas de aula por semana"
            )

        submitted = st.form_submit_button("💾 Salvar Disciplina", use_container_width=True)

        if submitted:
            if not nome or not professor:
                st.error("⚠️ Por favor, preencha o nome da disciplina e o professor.")
            else:
                # ── Verificação de duplicata ──────────────────────────────
                existing = make_xano_request('/subjects') or []
                is_duplicate = any(
                    s.get('name', '').strip().lower() == nome.strip().lower()
                    and s.get('professor', '').strip().lower() == professor.strip().lower()
                    for s in existing
                )
                if is_duplicate:
                    st.error(f"⚠️ A disciplina **{nome}** com o professor **{professor}** já está cadastrada.")
                else:
                    disciplina_data = {
                        "name": nome,
                        "professor": professor,
                        "day_of_week": dia_semana,
                        "carga_horaria": int(carga_horaria)
                    }
                    result = make_xano_request('/subjects', method='POST', data=disciplina_data)
                    if result:
                        st.success(f"✅ Disciplina **{nome}** cadastrada com sucesso!")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao cadastrar disciplina. Verifique os dados e tente novamente.")

# ══════════════════════════════════════════════════════════════════════════════
# ABA: LISTAR DISCIPLINAS
# ══════════════════════════════════════════════════════════════════════════════
with tab_lista:
    # Buscar todas as disciplinas e tarefas
    subjects = make_xano_request('/subjects') or []
    tasks_all = make_xano_request('/academic_tasks') or []

    from datetime import datetime
    now = datetime.now()

    # ── Construir set de subject_ids com tarefas atrasadas ──────────────────
    overdue_subject_ids = set()
    for t in tasks_all:
        if t.get('status') != 'completed' and t.get('due_date'):
            try:
                due = datetime.fromisoformat(t['due_date'].split('T')[0])
                if due < now:
                    overdue_subject_ids.add(t.get('subject_id'))
            except Exception:
                pass

    # ── Barra de pesquisa e filtros ─────────────────────────────────────────
    col_search, col_filter, col_refresh = st.columns([4, 2, 1])
    with col_search:
        search_term = st.text_input("🔍 Buscar disciplina", placeholder="Digite o nome da disciplina...")
    with col_filter:
        show_overdue_only = st.checkbox("⚠️ Apenas com tarefas em atraso")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄", help="Recarregar lista"):
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Aplicar filtros ─────────────────────────────────────────────────────
    filtered_subjects = subjects

    if search_term:
        filtered_subjects = [
            s for s in filtered_subjects
            if search_term.strip().lower() in s.get('name', '').lower()
        ]

    if show_overdue_only:
        filtered_subjects = [
            s for s in filtered_subjects
            if s.get('id') in overdue_subject_ids
        ]

    # ── Métricas rápidas ────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("📚 Total de Disciplinas", len(subjects))
    c2.metric("⚠️ Com Tarefas em Atraso", len(overdue_subject_ids))
    c3.metric("🔍 Resultados Filtrados", len(filtered_subjects))

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Lista de Disciplinas ─────────────────────────────────────────────────
    if not filtered_subjects:
        if search_term or show_overdue_only:
            st.info("🔍 Nenhuma disciplina encontrada com os filtros aplicados.")
        else:
            st.info("📭 Nenhuma disciplina cadastrada ainda. Use a aba **Nova Disciplina** para adicionar.")
    else:
        for subject in filtered_subjects:
            subject_id = subject.get('id')
            has_overdue = subject_id in overdue_subject_ids

            # ── Card de exibição ──────────────────────────────────────────
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 2])

                with col1:
                    name_display = subject.get('name', 'N/A')
                    if has_overdue:
                        st.markdown(f"**{name_display}** <span class='badge badge-red'>⚠️ Atrasada</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{name_display}**")
                    st.caption(f"👨‍🏫 {subject.get('professor', 'N/A')}")

                with col2:
                    st.write(f"📅 {subject.get('day_of_week', '—')}")

                with col3:
                    carga = subject.get('carga_horaria', subject.get('workload', '—'))
                    st.write(f"⏱️ {carga}h" if carga and carga != '—' else "⏱️ —")

                with col4:
                    # Contar tarefas desta disciplina
                    subj_tasks = [t for t in tasks_all if t.get('subject_id') == subject_id]
                    done = len([t for t in subj_tasks if t.get('status') == 'completed'])
                    st.write(f"📝 {done}/{len(subj_tasks)}")

                with col5:
                    btn_col1, btn_col2 = st.columns(2)

                    if btn_col1.button("✏️ Editar", key=f"edit_{subject_id}", use_container_width=True):
                        st.session_state[f'editing_{subject_id}'] = True

                    if btn_col2.button("🗑️ Excluir", key=f"del_{subject_id}", use_container_width=True):
                        st.session_state[f'deleting_{subject_id}'] = True

                # ── Formulário de Edição (inline) ──────────────────────────
                if st.session_state.get(f'editing_{subject_id}'):
                    with st.expander("✏️ Editando disciplina...", expanded=True):
                        with st.form(key=f"edit_form_{subject_id}"):
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                new_name = st.text_input("Nome", value=subject.get('name', ''))
                                new_professor = st.text_input("Professor", value=subject.get('professor', ''))
                            with ec2:
                                dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
                                try:
                                    cur_day_idx = dias.index(subject.get('day_of_week', 'Seg'))
                                except ValueError:
                                    cur_day_idx = 0
                                new_day = st.selectbox("Dia", dias, index=cur_day_idx)
                                cur_carga = subject.get('carga_horaria', subject.get('workload', 2))
                                try:
                                    cur_carga = int(cur_carga)
                                except (TypeError, ValueError):
                                    cur_carga = 2
                                new_carga = st.number_input("Carga Horária (h/sem)", min_value=0, max_value=20, value=cur_carga, step=1)

                            col_save, col_cancel = st.columns(2)
                            save_clicked = col_save.form_submit_button("💾 Salvar", use_container_width=True)
                            cancel_clicked = col_cancel.form_submit_button("✖ Cancelar", use_container_width=True)

                            if save_clicked:
                                if not new_name or not new_professor:
                                    st.error("Nome e professor são obrigatórios.")
                                else:
                                    update_data = {
                                        "name": new_name,
                                        "professor": new_professor,
                                        "day_of_week": new_day,
                                        "carga_horaria": int(new_carga)
                                    }
                                    result = make_xano_request(f"/subjects/{subject_id}", method='PATCH', data=update_data)
                                    if result:
                                        st.toast(f"✅ Disciplina '{new_name}' atualizada!")
                                        st.session_state.pop(f'editing_{subject_id}', None)
                                        st.rerun()
                                    else:
                                        st.error("❌ Falha ao atualizar.")

                            if cancel_clicked:
                                st.session_state.pop(f'editing_{subject_id}', None)
                                st.rerun()

                # ── Confirmação de Exclusão (inline) ──────────────────────
                if st.session_state.get(f'deleting_{subject_id}'):
                    with st.container():
                        st.warning(f"⚠️ Tem certeza que deseja excluir **{subject.get('name')}**? Esta ação não pode ser desfeita.")
                        cc1, cc2 = st.columns(2)
                        if cc1.button("✅ Confirmar Exclusão", key=f"confirm_del_{subject_id}", type="primary"):
                            make_xano_request(f"/subjects/{subject_id}", method='DELETE')
                            st.toast(f"🗑️ Disciplina '{subject.get('name')}' excluída.")
                            st.session_state.pop(f'deleting_{subject_id}', None)
                            st.rerun()
                        if cc2.button("✖ Cancelar", key=f"cancel_del_{subject_id}"):
                            st.session_state.pop(f'deleting_{subject_id}', None)
                            st.rerun()

                st.markdown('<hr class="divider">', unsafe_allow_html=True)