import streamlit as st
from utils.api import make_xano_request
import pandas as pd
from datetime import datetime

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="Disciplinas - EduTrack AI", page_icon="📚", layout="wide")
# ── Auth Guard ──────────────────────────────────────────────────────────────
if 'auth_token' not in st.session_state or not st.session_state.get('auth_token'):
    st.warning("⚠️ Você precisa fazer o login para acessar esta página.")
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
.badge-blue   { background: #DBEAFE; color: #1D4ED8; }
.badge-red    { background: #FEE2E2; color: #DC2626; }
.badge-green  { background: #D1FAE5; color: #065F46; }
.badge-gray   { background: #F3F4F6; color: #6B7280; }
.divider { border: none; border-top: 1px solid #F3F4F6; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

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
            semestre = st.text_input("Semestre/Período", placeholder="Ex: 2024.1")
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
                        "carga_horaria": int(carga_horaria),
                        "semester": semestre
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
    subjects = make_xano_request('/subjects') or []
    tasks_all = make_xano_request('/academic_tasks') or []

    now = datetime.now()

    # ── Identificar disciplinas com tarefas atrasadas ────────────────────────
    overdue_subject_ids = set()
    for t in tasks_all:
        if t.get('status') != 'completed' and t.get('due_date'):
            try:
                due = datetime.fromisoformat(t['due_date'].split('T')[0])
                if due < now:
                    overdue_subject_ids.add(t.get('subject_id'))
            except (ValueError, TypeError):
                pass

    # Separar ativas e arquivadas
    active_subjects   = [s for s in subjects if not s.get('archived')]
    archived_subjects = [s for s in subjects if s.get('archived') == True]

    # ── Barra de pesquisa e filtros ─────────────────────────────────────────
    col_search, col_filter, col_arch_filter, col_refresh = st.columns([3, 2, 2, 1])
    with col_search:
        search_term = st.text_input("🔍 Buscar disciplina", placeholder="Digite o nome da disciplina...")
    with col_filter:
        show_overdue_only = st.checkbox("⚠️ Apenas com tarefas em atraso")
    with col_arch_filter:
        show_archived = st.checkbox("📦 Incluir arquivadas")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄", help="Recarregar lista"):
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Aplicar filtros ─────────────────────────────────────────────────────
    filtered_subjects = subjects if show_archived else active_subjects

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
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 Disciplinas Ativas", len(active_subjects))
    c2.metric("📦 Arquivadas", len(archived_subjects))
    c3.metric("⚠️ Com Tarefas em Atraso", len(overdue_subject_ids))
    c4.metric("🔍 Resultados Filtrados", len(filtered_subjects))

    # --- Botão de Exportação ---
    if filtered_subjects:
        st.markdown("---")
        df_subjects = pd.DataFrame(filtered_subjects)
        col_map = {
            'name': 'Nome', 'professor': 'Professor', 'semester': 'Semestre',
            'day_of_week': 'Dia da Semana', 'carga_horaria': 'Carga Horária (h/sem)'
        }
        existing = [c for c in col_map if c in df_subjects.columns]
        df_export = df_subjects[existing].rename(columns=col_map)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
           label="📥 Exportar Disciplinas para CSV",
           data=csv,
           file_name='disciplinas_edutrack.csv',
           mime='text/csv'
        )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Lista de Disciplinas ─────────────────────────────────────────────────
    if not filtered_subjects:
        if search_term or show_overdue_only:
            st.info("🔍 Nenhuma disciplina encontrada com os filtros aplicados.")
        elif show_archived:
            st.info("📭 Nenhuma disciplina cadastrada ainda. Use a aba **Nova Disciplina** para adicionar.")
        else:
            if archived_subjects:
                st.info("📭 Nenhuma disciplina ativa. Marque **Incluir arquivadas** para ver as arquivadas.")
            else:
                st.info("📭 Nenhuma disciplina cadastrada ainda. Use a aba **Nova Disciplina** para adicionar.")
    else:
        for subject in filtered_subjects:
            subject_id = subject.get('id')
            has_overdue = subject_id in overdue_subject_ids
            is_archived = subject.get('archived') == True

            # ── Card de exibição ──────────────────────────────────────────
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 2])

                with col1:
                    name_display = subject.get('name', 'N/A')
                    if is_archived:
                        st.markdown(
                            f"**{name_display}** <span class='badge badge-gray'>📦 Arquivada</span>",
                            unsafe_allow_html=True
                        )
                    elif has_overdue:
                        st.markdown(
                            f"**{name_display}** <span class='badge badge-red'>⚠️ Atrasada</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(f"**{name_display}**")
                    st.caption(f"👨‍🏫 {subject.get('professor', 'N/A')}  •  🗓️ {subject.get('semester', 'N/A')}")

                with col2:
                    st.write(f"📅 {subject.get('day_of_week', '—')}")

                with col3:
                    carga = subject.get('carga_horaria', subject.get('workload', '—'))
                    st.write(f"⏱️ {carga}h" if carga and carga != '—' else "⏱️ —")

                with col4:
                    subj_tasks = [t for t in tasks_all if t.get('subject_id') == subject_id]
                    done = len([t for t in subj_tasks if t.get('status') == 'completed'])
                    st.write(f"📝 {done}/{len(subj_tasks)}")

                with col5:
                    if not is_archived:
                        btn_edit, btn_arch = st.columns(2)
                        if btn_edit.button("✏️ Editar", key=f"edit_{subject_id}", use_container_width=True):
                            st.session_state[f'editing_{subject_id}'] = True
                        if btn_arch.button("📦 Arquivar", key=f"arch_{subject_id}", use_container_width=True):
                            st.session_state[f'archiving_{subject_id}'] = True
                    else:
                        if st.button("↩️ Restaurar", key=f"restore_{subject_id}", use_container_width=True):
                            st.session_state[f'restoring_{subject_id}'] = True

                    if st.button("🗑️ Excluir", key=f"del_{subject_id}", use_container_width=True):
                        st.session_state[f'deleting_{subject_id}'] = True

                # ── Formulário de Edição (inline) ──────────────────────────
                if st.session_state.get(f'editing_{subject_id}'):
                    with st.expander("✏️ Editando disciplina...", expanded=True):
                        with st.form(key=f"edit_form_{subject_id}"):
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                new_name = st.text_input("Nome", value=subject.get('name', ''))
                                new_professor = st.text_input("Professor", value=subject.get('professor', ''))
                                new_semester = st.text_input("Semestre/Período", value=subject.get('semester', ''))
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
                                        "carga_horaria": int(new_carga),
                                        "semester": new_semester
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

                # ── Confirmação de Arquivamento ────────────────────────────
                if st.session_state.get(f'archiving_{subject_id}'):
                    with st.container():
                        st.warning(
                            f"📦 Arquivar **{subject.get('name')}**? "
                            "Ela ficará oculta da lista principal e não contará nas métricas ativas."
                        )
                        ac1, ac2 = st.columns(2)
                        if ac1.button("📦 Confirmar Arquivo", key=f"confirm_arch_{subject_id}", type="primary"):
                            result = make_xano_request(f"/subjects/{subject_id}", method='PATCH', data={"archived": True})
                            if result is not None:
                                st.toast(f"📦 '{subject.get('name')}' arquivada.")
                                st.session_state.pop(f'archiving_{subject_id}', None)
                                st.rerun()
                            else:
                                st.error("❌ Falha ao arquivar. Verifique se o campo `archived` (boolean) existe na tabela `subjects` do Xano.")
                        if ac2.button("✖ Cancelar", key=f"cancel_arch_{subject_id}"):
                            st.session_state.pop(f'archiving_{subject_id}', None)
                            st.rerun()

                # ── Confirmação de Restauração ─────────────────────────────
                if st.session_state.get(f'restoring_{subject_id}'):
                    with st.container():
                        st.info(f"↩️ Restaurar **{subject.get('name')}** para a lista ativa?")
                        rc1, rc2 = st.columns(2)
                        if rc1.button("↩️ Confirmar Restauração", key=f"confirm_rest_{subject_id}", type="primary"):
                            result = make_xano_request(f"/subjects/{subject_id}", method='PATCH', data={"archived": False})
                            if result is not None:
                                st.toast(f"↩️ '{subject.get('name')}' restaurada.")
                                st.session_state.pop(f'restoring_{subject_id}', None)
                                st.rerun()
                            else:
                                st.error("❌ Falha ao restaurar.")
                        if rc2.button("✖ Cancelar", key=f"cancel_rest_{subject_id}"):
                            st.session_state.pop(f'restoring_{subject_id}', None)
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
