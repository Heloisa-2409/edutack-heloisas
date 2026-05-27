import streamlit as st
from datetime import datetime
import unicodedata
from utils.api import make_xano_request
from utils.styles import apply_global_styles
import pandas as pd
from fpdf import FPDF

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="Tarefas - EduTrack AI", page_icon="📝", layout="wide")
apply_global_styles()
if 'auth_token' not in st.session_state or not st.session_state.get('auth_token'):
    st.switch_page("pages/0_🔐_Login.py")

# ── Estilo Premium ──────────────────────────────────────────────────────────
st.markdown("""
<style>
.group-header { font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 700; color: #2563A8; margin-top: 1rem; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Status helpers ──────────────────────────────────────────────────────────
STATUS_LABELS = {
    "pending":     ("🟡", "Pendente",     "status-pending"),
    "in_progress": ("🟠", "Em Andamento", "status-progress"),
    "completed":   ("🟢", "Concluída",    "status-done"),
}

PRIORITY_LABELS = {
    "low":    ("⬇️", "Baixa"),
    "medium": ("⏺️", "Média"),
    "high":   ("⬆️", "Alta"),
}

def format_status(status: str) -> str:
    icon, label, css = STATUS_LABELS.get(status, ("⚪", status, "status-pending"))
    return f'<span class="{css}">{icon} {label}</span>'

def get_days_left(due_date_str: str | None):
    if not due_date_str:
        return None
    try:
        due = datetime.fromisoformat(due_date_str.split('T')[0])
        return (due - datetime.now()).days
    except Exception:
        return None

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-header">📝 Gestão de Tarefas</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Organize, edite e acompanhe todas as suas tarefas acadêmicas</p>', unsafe_allow_html=True)

# ── Buscar dados base ────────────────────────────────────────────────────────
subjects = make_xano_request('/subjects') or []
subjects_map = {s['id']: s['name'] for s in subjects}
subjects_options = {s['name']: s['id'] for s in subjects}

# ── Abas ────────────────────────────────────────────────────────────────────
tab_lista, tab_novo = st.tabs(["📋 Minhas Tarefas", "➕ Nova Tarefa"])

# ══════════════════════════════════════════════════════════════════════════════
# ABA: NOVA TAREFA
# ══════════════════════════════════════════════════════════════════════════════
with tab_novo:
    st.subheader("Criar Nova Tarefa")

    if not subjects_options:
        st.warning("⚠️ Você precisa cadastrar ao menos uma disciplina antes de criar tarefas.")
    else:
        with st.form("form_tarefa", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                title = st.text_input("Título da Tarefa *", placeholder="Ex: Estudar capítulo 5")
                subject_name_sel = st.selectbox("Disciplina *", options=list(subjects_options.keys()))
                status_new = st.selectbox(
                    "Status Inicial",
                    ["pending", "in_progress", "completed"],
                    format_func=lambda x: STATUS_LABELS[x][1]
                )
            with col_b:
                description = st.text_area("Descrição", placeholder="Descreva os detalhes da tarefa...")
                due_date = st.date_input("Prazo de Entrega *", min_value=datetime.today().date())
                priority_new = st.selectbox(
                    "Prioridade",
                    ["low", "medium", "high"],
                    index=1,
                    format_func=lambda x: PRIORITY_LABELS[x][1]
                )

            submitted = st.form_submit_button("✅ Criar Tarefa", use_container_width=True)

            if submitted:
                if title and subject_name_sel:
                    task_data = {
                        "title": title,
                        "description": description,
                        "subject_id": subjects_options[subject_name_sel],
                        "due_date": due_date.isoformat(),
                        "status": status_new,
                        "priority": priority_new
                    }
                    result = make_xano_request('/academic_tasks', method='POST', data=task_data)
                    if result:
                        st.success(f"✅ Tarefa **{title}** criada com sucesso!")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao criar tarefa. Verifique os dados e tente novamente.")
                else:
                    st.error("⚠️ Preencha o título e selecione uma disciplina.")

# ══════════════════════════════════════════════════════════════════════════════
# ABA: LISTAR TAREFAS
# ══════════════════════════════════════════════════════════════════════════════
with tab_lista:
    # ── Controles de filtro e agrupamento ────────────────────────────────────
    col_search, col_status, col_group = st.columns([3, 2, 2])
    with col_search:
        search = st.text_input("🔍 Buscar tarefa...", placeholder="Título ou descrição...")
    with col_status:
        status_filter = st.selectbox("Status", ["Todas", "pending", "in_progress", "completed"],
                                     format_func=lambda x: "Todas" if x == "Todas" else STATUS_LABELS[x][1])
    with col_group:
        group_by = st.selectbox("Agrupar por", ["Sem Agrupamento", "Disciplina", "Prazo"])

    tasks = make_xano_request('/academic_tasks') or []

    # ── Aplicar filtros ──────────────────────────────────────────────────────
    filtered = tasks

    if search:
        q = search.strip().lower()
        filtered = [t for t in filtered if q in t.get('title', '').lower() or q in t.get('description', '').lower()]

    if status_filter != "Todas":
        filtered = [t for t in filtered if t.get('status') == status_filter]

    # ── Métricas rápidas ──────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    total = len(filtered)
    done_c  = len([t for t in filtered if t.get('status') == 'completed'])
    pend_c  = len([t for t in filtered if t.get('status') == 'pending'])
    over_c  = len([t for t in filtered if t.get('status') != 'completed' and get_days_left(t.get('due_date')) is not None and get_days_left(t.get('due_date')) < 0])

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("📋 Total", total)
    mc2.metric("✅ Concluídas", done_c)
    mc3.metric("⏳ Pendentes", pend_c)
    mc4.metric("⚠️ Atrasadas", over_c)

    # --- Exportação ---
    if filtered:
        st.markdown("---")

        def _strip(text):
            if not isinstance(text, str):
                return str(text) if text is not None else ''
            return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

        def gerar_pdf_tarefas(data, smap):
            STATUS_PT = {"pending": "Pendente", "in_progress": "Em Andamento", "completed": "Concluida"}
            PRIO_PT   = {"low": "Baixa", "medium": "Media", "high": "Alta"}
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "EduTrack AI - Tarefas", ln=1, align="C")
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 6, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1, align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(4)

            col_w = [55, 38, 25, 32, 25, 15]
            headers = ["Titulo", "Disciplina", "Prazo", "Status", "Prioridade", "Dias"]
            pdf.set_fill_color(30, 58, 138)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 9)
            for h, w in zip(headers, col_w):
                pdf.cell(w, 8, h, border=1, fill=True)
            pdf.ln()
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 9)
            for t in data:
                due_str = ''
                days_str = ''
                if t.get('due_date'):
                    try:
                        d = datetime.fromisoformat(t['due_date'].split('T')[0])
                        due_str = d.strftime('%d/%m/%Y')
                        days_left = (d.date() - datetime.today().date()).days
                        days_str = str(days_left)
                    except Exception:
                        due_str = t['due_date'][:10]
                row = [
                    _strip(t.get('title', ''))[:32],
                    _strip(smap.get(t.get('subject_id'), ''))[:22],
                    due_str,
                    _strip(STATUS_PT.get(t.get('status', ''), t.get('status', '')))[:15],
                    _strip(PRIO_PT.get(t.get('priority', 'medium'), 'Media')),
                    days_str,
                ]
                for val, w in zip(row, col_w):
                    pdf.cell(w, 7, val, border=1)
                pdf.ln()
            return bytes(pdf.output())

        df_tasks = pd.DataFrame(filtered)
        df_tasks['disciplina'] = df_tasks['subject_id'].map(subjects_map).fillna('N/A')
        df_tasks['prazo'] = pd.to_datetime(df_tasks['due_date'], errors='coerce').dt.strftime('%d/%m/%Y')
        df_tasks['status_label'] = df_tasks['status'].map(lambda x: STATUS_LABELS.get(x, ('', x))[1])
        if 'priority' in df_tasks.columns:
            df_tasks['priority_label'] = df_tasks['priority'].map(lambda x: PRIORITY_LABELS.get(x, ('', x))[1])
        else:
            df_tasks['priority_label'] = 'N/A'
        df_export = df_tasks[['title', 'disciplina', 'prazo', 'status_label', 'priority_label', 'description']]
        df_export.columns = ['Título', 'Disciplina', 'Prazo', 'Status', 'Prioridade', 'Descrição']
        csv = df_export.to_csv(index=False).encode('utf-8')

        ex_col1, ex_col2 = st.columns(2)
        ex_col1.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name='tarefas_edutrack.csv',
            mime='text/csv',
            use_container_width=True
        )
        try:
            pdf_bytes = gerar_pdf_tarefas(filtered, subjects_map)
            ex_col2.download_button(
                label="📄 Exportar PDF",
                data=pdf_bytes,
                file_name='tarefas_edutrack.pdf',
                mime='application/pdf',
                use_container_width=True
            )
        except Exception as e:
            ex_col2.error(f"Erro ao gerar PDF: {e}")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if not filtered:
        st.info("🔍 Nenhuma tarefa encontrada com os filtros aplicados.")
    else:
        # ── Agrupar tarefas ──────────────────────────────────────────────────
        if group_by == "Disciplina":
            groups: dict = {}
            for t in filtered:
                label = subjects_map.get(t.get('subject_id'), "Sem disciplina")
                groups.setdefault(label, []).append(t)
        elif group_by == "Prazo":
            groups = {"⚠️ Atrasadas": [], "📅 Hoje": [], "📆 Esta Semana": [], "🗓️ Futuras": [], "❓ Sem Prazo": []}
            for t in filtered:
                dl = get_days_left(t.get('due_date'))
                if dl is None:
                    groups["❓ Sem Prazo"].append(t)
                elif dl < 0:
                    groups["⚠️ Atrasadas"].append(t)
                elif dl == 0:
                    groups["📅 Hoje"].append(t)
                elif dl <= 7:
                    groups["📆 Esta Semana"].append(t)
                else:
                    groups["🗓️ Futuras"].append(t)
        else:
            groups = {"": filtered}

        # ── Renderizar grupos ────────────────────────────────────────────────
        for group_name, group_tasks in groups.items():
            if not group_tasks:
                continue

            if group_name:
                st.markdown(f'<p class="group-header">📂 {group_name} ({len(group_tasks)})</p>', unsafe_allow_html=True)

            for task in group_tasks:
                task_id = task.get('id')
                task_title = task.get('title', 'Sem título')
                task_status = task.get('status', 'pending')
                task_due = task.get('due_date')
                days_left = get_days_left(task_due)
                is_overdue = days_left is not None and days_left < 0 and task_status != 'completed'

                icon = STATUS_LABELS.get(task_status, ("⚪",))[0]
                if is_overdue:
                    icon = "🔴"

                with st.expander(f"{icon} {task_title}", expanded=False):
                    c_info, c_actions = st.columns([3, 1])

                    with c_info:
                        subj_name = subjects_map.get(task.get('subject_id'), "Desconhecida")
                        st.markdown(f"**📚 Disciplina:** {subj_name}")

                        task_priority = task.get('priority', 'medium')
                        p_icon, p_label = PRIORITY_LABELS.get(task_priority, ("⏺️", "Média"))
                        st.markdown(f"**Prioridade:** {p_icon} {p_label}")

                        if task_due:
                            try:
                                due_dt = datetime.fromisoformat(task_due.split('T')[0])
                                st.markdown(f"**📅 Prazo:** {due_dt.strftime('%d/%m/%Y')}")
                            except Exception:
                                st.markdown(f"**📅 Prazo:** {task_due}")

                        if days_left is not None and task_status != 'completed':
                            if days_left < 0:
                                st.error(f"⚠️ Atrasada há **{abs(days_left)} dias**")
                            elif days_left == 0:
                                st.warning("📅 Vence **hoje**!")
                            else:
                                st.info(f"⏰ Faltam **{days_left} dias**")

                        st.markdown(format_status(task_status), unsafe_allow_html=True)

                        if task.get('description'):
                            st.markdown(f"**📄 Descrição:** {task['description']}")

                    with c_actions:
                        # ── Concluir ─────────────────────────────────────
                        if task_status != 'completed':
                            if st.button("✅ Concluir", key=f"done_{task_id}", use_container_width=True):
                                due_raw = task.get('due_date') or ''
                                due_iso = due_raw[:10] if len(due_raw) >= 10 else datetime.today().date().isoformat()
                                patch_data = {"status": "completed", "due_date": due_iso}
                                result = make_xano_request(f'/academic_tasks/{task_id}', method='PATCH', data=patch_data)
                                if result is not None:
                                    st.toast("✅ Tarefa marcada como concluída!")
                                    st.rerun()

                        # ── Editar (toggle) ───────────────────────────────
                        if st.button("✏️ Editar", key=f"edit_{task_id}", use_container_width=True):
                            editing_key = f'editing_task_{task_id}'
                            st.session_state[editing_key] = not st.session_state.get(editing_key, False)
                            st.rerun()

                        # ── Excluir (confirmar) ───────────────────────────
                        if st.button("🗑️ Excluir", key=f"del_{task_id}", use_container_width=True):
                            st.session_state[f'confirm_del_task_{task_id}'] = True
                            st.rerun()

                    # ── Formulário de Edição ──────────────────────────────
                    if st.session_state.get(f'editing_task_{task_id}'):
                        st.markdown('<hr class="divider">', unsafe_allow_html=True)
                        st.markdown("#### ✏️ Editando tarefa")
                        with st.form(key=f"edit_task_form_{task_id}"):
                            ef1, ef2 = st.columns(2)
                            with ef1:
                                new_title = st.text_input("Título", value=task.get('title', ''))
                                cur_subj_name = subjects_map.get(task.get('subject_id'), '')
                                new_subj = st.selectbox(
                                    "Disciplina",
                                    options=list(subjects_options.keys()),
                                    index=list(subjects_options.keys()).index(cur_subj_name) if cur_subj_name in subjects_options else 0
                                )
                                new_status = st.selectbox(
                                    "Status",
                                    ["pending", "in_progress", "completed"],
                                    index=["pending", "in_progress", "completed"].index(task.get('status', 'pending')),
                                    format_func=lambda x: STATUS_LABELS[x][1]
                                )
                            with ef2:
                                new_desc = st.text_area("Descrição", value=task.get('description', ''))
                                try:
                                    cur_due = datetime.fromisoformat(task.get('due_date', '').split('T')[0]).date() if task.get('due_date') else datetime.today().date()
                                except Exception:
                                    cur_due = datetime.today().date()
                                new_due = st.date_input("Prazo", value=cur_due)
                                new_priority = st.selectbox(
                                    "Prioridade",
                                    ["low", "medium", "high"],
                                    index=["low", "medium", "high"].index(task.get('priority', 'medium')),
                                    format_func=lambda x: PRIORITY_LABELS[x][1]
                                )

                            es1, es2 = st.columns(2)
                            save_e = es1.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                            cancel_e = es2.form_submit_button("✖ Cancelar", use_container_width=True)

                            if save_e:
                                update_data = {
                                    "title": new_title,
                                    "description": new_desc,
                                    "subject_id": subjects_options.get(new_subj, task.get('subject_id')),
                                    "due_date": new_due.isoformat(),
                                    "status": new_status,
                                    "priority": new_priority
                                }
                                result = make_xano_request(f'/academic_tasks/{task_id}', method='PATCH', data=update_data)
                                if result:
                                    st.toast(f"✅ Tarefa '{new_title}' atualizada!")
                                    st.session_state.pop(f'editing_task_{task_id}', None)
                                    st.rerun()
                                else:
                                    st.error("❌ Falha ao salvar.")

                            if cancel_e:
                                st.session_state.pop(f'editing_task_{task_id}', None)
                                st.rerun()

                    # ── Confirmação de Exclusão ───────────────────────────
                    if st.session_state.get(f'confirm_del_task_{task_id}'):
                        st.markdown('<hr class="divider">', unsafe_allow_html=True)
                        st.warning(f"⚠️ Confirmar exclusão de **{task_title}**?")
                        dc1, dc2 = st.columns(2)
                        if dc1.button("✅ Sim, excluir", key=f"yes_del_{task_id}", type="primary"):
                            make_xano_request(f'/academic_tasks/{task_id}', method='DELETE')
                            st.toast(f"🗑️ Tarefa '{task_title}' excluída.")
                            st.session_state.pop(f'confirm_del_task_{task_id}', None)
                            st.rerun()
                        if dc2.button("✖ Cancelar", key=f"no_del_{task_id}"):
                            st.session_state.pop(f'confirm_del_task_{task_id}', None)
                            st.rerun()
