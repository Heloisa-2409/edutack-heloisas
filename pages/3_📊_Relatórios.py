import streamlit as st
import pandas as pd
import unicodedata
from datetime import datetime, date, timedelta
from fpdf import FPDF
from utils.api import make_xano_request
from utils.styles import apply_global_styles

st.set_page_config(page_title="Relatórios - EduTrack AI", page_icon="📊", layout="wide")
apply_global_styles()

# ── Auth Guard ──────────────────────────────────────────────────────────────
if 'auth_token' not in st.session_state or not st.session_state.get('auth_token'):
    st.switch_page("pages/0_🔐_Login.py")

# ── Cabeçalho ───────────────────────────────────────────────────────────────
user_name = st.session_state.get('user', {}).get('name', 'Estudante').split()[0]
now = datetime.now()
hour = now.hour
greeting = "Bom dia" if hour < 12 else ("Boa tarde" if hour < 18 else "Boa noite")

st.markdown(f'<h1 class="page-header">🎓 {greeting}, {user_name}!</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Aqui está seu resumo acadêmico e relatórios de progresso.</p>', unsafe_allow_html=True)

# ── Carregar Dados ──────────────────────────────────────────────────────────
with st.spinner("Carregando seus dados..."):
    subjects = make_xano_request('/subjects') or []
    tasks = make_xano_request('/academic_tasks') or []
    subjects_map = {s['id']: s['name'] for s in subjects}

if not subjects and not tasks:
    st.markdown("""
    <div style="text-align:center; padding:3rem 2rem; background:linear-gradient(135deg,#EFF6FF,#F0FDF4);
                border-radius:16px; margin-top:1.5rem; border:1px solid #C5D8EC;">
        <h2 style="font-family:'Outfit',sans-serif; color:#1A3A5C; font-size:1.6rem;">👋 Bem-vindo ao EduTrack AI!</h2>
        <p style="color:#5A7A9A; font-size:1rem; margin-top:0.5rem;">
            Você ainda não tem disciplinas ou tarefas cadastradas.<br>
            Use o menu lateral para começar adicionando suas <strong>Disciplinas</strong> e depois suas <strong>Tarefas</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO: MÉTRICAS RÁPIDAS (DASHBOARD)
# ══════════════════════════════════════════════════════════════════════════════
active_subjects = [s for s in subjects if not s.get('archived')]
total_tasks     = len(tasks)
completed_tasks = [t for t in tasks if t.get('status') == 'completed']
pending_tasks   = [t for t in tasks if t.get('status') == 'pending']
progress_pct    = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0

def _safe_due(t):
    try:
        return datetime.fromisoformat(t['due_date'].split('T')[0])
    except Exception:
        return None

overdue = [t for t in tasks if t.get('status') != 'completed' and _safe_due(t) and _safe_due(t) < now]
upcoming = sorted(
    [t for t in tasks if t.get('status') != 'completed' and _safe_due(t) and _safe_due(t) >= now],
    key=lambda t: _safe_due(t)
)[:5]

mc1, mc2, mc3, mc4, mc5 = st.columns(5)
mc1.metric("📚 Disciplinas Ativas", len(active_subjects))
mc2.metric("📋 Total Tarefas", total_tasks)
mc3.metric("⏳ Pendentes", len(pending_tasks))
mc4.metric("⚠️ Atrasadas", len(overdue), delta=f"-{len(overdue)}" if overdue else None, delta_color="inverse")
mc5.metric("✅ Progresso", f"{progress_pct:.0f}%")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Próximas tarefas ─────────────────────────────────────────────────────────
if upcoming:
    st.markdown('<h2 class="section-header">📅 Próximas Tarefas</h2>', unsafe_allow_html=True)
    for t in upcoming:
        due = _safe_due(t)
        days_left = (due.date() - now.date()).days if due else 0
        subj_name = subjects_map.get(t.get('subject_id'), 'N/A')
        days_txt = "Vence hoje!" if days_left == 0 else (f"Amanhã" if days_left == 1 else f"{days_left} dias")
        color = "#EF4444" if days_left == 0 else ("#F59E0B" if days_left <= 2 else "#5B9BD5")
        st.markdown(f"""
        <div style="background:#fff; border:1px solid #C5D8EC; border-left:4px solid {color};
                    border-radius:10px; padding:0.7rem 1.1rem; margin-bottom:0.4rem;">
            <strong>{t.get('title','')}</strong>
            <span style="color:#5A7A9A; font-size:0.85rem;"> · 📚 {subj_name} · ⏰ {days_txt}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO: PROGRESSO POR DISCIPLINA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h2 class="section-header">🚀 Progresso por Disciplina</h2>', unsafe_allow_html=True)

if not subjects:
    st.warning("Nenhuma disciplina cadastrada para exibir o progresso.")
else:
    progress_data = []
    for subject in subjects:
        subject_id = subject['id']
        subject_tasks = [t for t in tasks if t.get('subject_id') == subject_id]
        total_count = len(subject_tasks)
        completed_count = len([t for t in subject_tasks if t.get('status') == 'completed'])
        progress = (completed_count / total_count) if total_count > 0 else 0
        progress_data.append({
            "name": subject.get('name', 'N/A'),
            "total": total_count,
            "completed": completed_count,
            "progress": progress
        })

    for data in sorted(progress_data, key=lambda x: x['name']):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{data['name']}**")
                st.progress(data['progress'])
            with col2:
                st.metric(label="Tarefas Concluídas", value=f"{data['completed']}/{data['total']}")

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO: HISTÓRICO DE TAREFAS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h2 class="section-header">🗓️ Histórico de Tarefas por Período</h2>', unsafe_allow_html=True)

filtered_tasks = []
if not tasks:
    st.warning("Nenhuma tarefa cadastrada para exibir o histórico.")
else:
    today = date.today()
    try:
        last_month_start = today.replace(day=1) - timedelta(days=1)
        start_default = last_month_start.replace(day=1)
    except ValueError:
        start_default = today.replace(day=1) - timedelta(days=30)

    f_col1, f_col2 = st.columns(2)
    start_date = f_col1.date_input("Data de Início", value=start_default)
    end_date = f_col2.date_input("Data de Fim", value=today)

    if start_date > end_date:
        st.error("A data de início não pode ser posterior à data de fim.")
        st.stop()
    else:
        for task in tasks:
            if task.get('due_date'):
                try:
                    task_due_date = datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                    if start_date <= task_due_date <= end_date:
                        filtered_tasks.append(task)
                except (ValueError, TypeError):
                    continue

        if not filtered_tasks:
            st.info("Nenhuma tarefa encontrada no período selecionado.")
        else:
            STATUS_LABELS = {"pending": "Pendente", "in_progress": "Em Andamento", "completed": "Concluída"}
            df_tasks = pd.DataFrame(filtered_tasks)
            df_tasks['disciplina'] = df_tasks['subject_id'].map(subjects_map).fillna('N/A')
            df_tasks['prazo'] = pd.to_datetime(df_tasks['due_date'], errors='coerce').dt.strftime('%d/%m/%Y')
            df_tasks['status_label'] = df_tasks['status'].map(STATUS_LABELS).fillna(df_tasks['status'])
            df_display = df_tasks[['title', 'disciplina', 'prazo', 'status_label']].copy()
            df_display.columns = ['Título', 'Disciplina', 'Prazo', 'Status']
            st.dataframe(df_display, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO: EXPORTAR DADOS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h2 class="section-header">📤 Exportar Dados</h2>', unsafe_allow_html=True)


def _strip(text):
    if not isinstance(text, str):
        return str(text) if text is not None else ''
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')


def gerar_pdf(subjects_data, tasks_data, smap):
    STATUS_PT = {"pending": "Pendente", "in_progress": "Em Andamento", "completed": "Concluida"}

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Título do relatório
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "EduTrack AI - Relatorio Academico", ln=1, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, f"Gerado em: {datetime.now().strftime('%d/%m/%Y as %H:%M')}", ln=1, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # ── Progresso por Disciplina ──────────────────────────────────────────────
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 9, "  Progresso por Disciplina", ln=1, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    w = [75, 38, 35, 32]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(219, 234, 254)
    pdf.cell(w[0], 7, "Disciplina", border=1, fill=True)
    pdf.cell(w[1], 7, "Professor", border=1, fill=True)
    pdf.cell(w[2], 7, "Tarefas", border=1, fill=True, align="C")
    pdf.cell(w[3], 7, "Progresso", border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for subj in sorted(subjects_data, key=lambda x: x.get('name', '')):
        sid = subj['id']
        st_list = [t for t in tasks_data if t.get('subject_id') == sid]
        total = len(st_list)
        done = len([t for t in st_list if t.get('status') == 'completed'])
        pct = int(done / total * 100) if total > 0 else 0
        pdf.cell(w[0], 7, _strip(subj.get('name', ''))[:42], border=1)
        pdf.cell(w[1], 7, _strip(subj.get('professor') or '')[:22], border=1)
        pdf.cell(w[2], 7, f"{done}/{total}", border=1, align="C")
        pdf.cell(w[3], 7, f"{pct}%", border=1, align="C")
        pdf.ln()

    pdf.ln(6)

    # ── Histórico de Tarefas ──────────────────────────────────────────────────
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 9, "  Historico de Tarefas", ln=1, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    tw = [65, 45, 28, 42]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(219, 234, 254)
    pdf.cell(tw[0], 7, "Titulo", border=1, fill=True)
    pdf.cell(tw[1], 7, "Disciplina", border=1, fill=True)
    pdf.cell(tw[2], 7, "Prazo", border=1, fill=True, align="C")
    pdf.cell(tw[3], 7, "Status", border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for task in sorted(tasks_data, key=lambda x: x.get('due_date') or ''):
        due_str = ''
        if task.get('due_date'):
            try:
                due_str = datetime.fromisoformat(task['due_date'].split('T')[0]).strftime('%d/%m/%Y')
            except Exception:
                due_str = task['due_date'][:10]
        pdf.cell(tw[0], 7, _strip(task.get('title', ''))[:38], border=1)
        pdf.cell(tw[1], 7, _strip(smap.get(task.get('subject_id'), ''))[:26], border=1)
        pdf.cell(tw[2], 7, due_str, border=1, align="C")
        pdf.cell(tw[3], 7, _strip(STATUS_PT.get(task.get('status', ''), task.get('status', ''))), border=1, align="C")
        pdf.ln()

    return bytes(pdf.output())


# ── Botões CSV ────────────────────────────────────────────────────────────────
ec1, ec2 = st.columns(2)

with ec1:
    if subjects:
        df_s = pd.DataFrame(subjects)
        col_map_s = {
            'name': 'Nome', 'professor': 'Professor', 'semester': 'Semestre',
            'day_of_week': 'Dia', 'carga_horaria': 'Carga (h/sem)'
        }
        existing_s = [c for c in col_map_s if c in df_s.columns]
        df_s_exp = df_s[existing_s].rename(columns=col_map_s)
        st.download_button(
            "📥 Baixar Disciplinas (CSV)",
            data=df_s_exp.to_csv(index=False).encode('utf-8'),
            file_name="disciplinas_edutrack.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("Sem disciplinas para exportar.")

with ec2:
    if tasks:
        df_t = pd.DataFrame(tasks)
        df_t['disciplina'] = df_t['subject_id'].map(subjects_map).fillna('N/A')
        df_t['prazo'] = pd.to_datetime(df_t['due_date'], errors='coerce').dt.strftime('%d/%m/%Y')
        STATUS_CSV = {"pending": "Pendente", "in_progress": "Em Andamento", "completed": "Concluida"}
        df_t['status_label'] = df_t['status'].map(STATUS_CSV).fillna(df_t['status'])
        df_t_exp = df_t[['title', 'disciplina', 'prazo', 'status_label']].copy()
        df_t_exp.columns = ['Titulo', 'Disciplina', 'Prazo', 'Status']
        st.download_button(
            "📥 Baixar Tarefas (CSV)",
            data=df_t_exp.to_csv(index=False).encode('utf-8'),
            file_name="tarefas_edutrack.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("Sem tarefas para exportar.")

# ── Botão PDF ─────────────────────────────────────────────────────────────────
st.markdown("---")
if subjects or tasks:
    try:
        pdf_bytes = gerar_pdf(subjects, tasks, subjects_map)
        st.download_button(
            "📄 Exportar Relatório Completo (PDF)",
            data=pdf_bytes,
            file_name=f"relatorio_edutrack_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
