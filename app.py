import streamlit as st
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Xano
XANO_WORKSPACE_URL = os.getenv('XANO_WORKSPACE_URL', 'https://x8ki-letl-twmt.xano.io/api')

# ── Configuração da Página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="EduTrack AI - Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Estilo Global Premium ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@700;800&display=swap');

html, body, .main, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Header */
.dashboard-hero {
    background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 60%, #60A5FA 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    color: white;
}
.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.2;
}
.hero-sub {
    font-size: 1rem;
    opacity: 0.85;
    margin-top: 0.4rem;
}

/* Metric cards */
.metric-card {
    background: white;
    border-radius: 14px;
    border: 1px solid #E5E7EB;
    padding: 1.25rem 1.5rem;
    text-align: center;
    transition: box-shadow 0.2s;
}
.metric-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.metric-value { font-family: 'Outfit', sans-serif; font-size: 2.5rem; font-weight: 800; line-height: 1; }
.metric-label { font-size: 0.85rem; color: #6B7280; margin-top: 0.3rem; font-weight: 500; }

/* Task cards */
.task-card {
    background: white;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    padding: 1rem 1.25rem;
    margin-bottom: 0.6rem;
    border-left: 4px solid #3B82F6;
}
.task-card.overdue { border-left-color: #EF4444; background: #FFF5F5; }
.task-card.today   { border-left-color: #F59E0B; background: #FFFBEB; }
.task-title { font-weight: 600; font-size: 0.95rem; color: #111827; }
.task-meta  { font-size: 0.8rem; color: #6B7280; margin-top: 0.2rem; }

/* Section header */
.section-header {
    font-family: 'Outfit', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #1E3A8A;
    margin-bottom: 0.75rem;
    margin-top: 1.5rem;
}
.divider { border: none; border-top: 1px solid #F3F4F6; margin: 1.5rem 0; }

/* Progress */
.progress-label { font-size: 0.85rem; color: #374151; font-weight: 500; margin-bottom: 0.25rem; }
.welcome-empty {
    text-align: center;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, #EFF6FF, #F0FDF4);
    border-radius: 16px;
    margin-top: 1.5rem;
}
.welcome-empty h2 { font-family: 'Outfit', sans-serif; color: #1E3A8A; font-size: 1.6rem; }
.welcome-empty p  { color: #6B7280; font-size: 1rem; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Função helper para API ──────────────────────────────────────────────────
def make_xano_request(endpoint, method='GET', data=None):
    """Faz uma requisição para a API Xano com handler de 401 automático."""
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
            st.rerun()

        if response.status_code == 204:
            return {"status": "success"}

        if response.ok:
            return response.json()

        response.raise_for_status()
        return None

    except requests.exceptions.RequestException:
        return None

def is_authenticated():
    return 'auth_token' in st.session_state and bool(st.session_state.get('auth_token'))

# ── Logout na sidebar ─────────────────────────────────────────────────────────
if is_authenticated():
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.pop('auth_token', None)
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if not is_authenticated():
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0 1rem 0;">
        <h1 style="font-family:'Outfit',sans-serif; font-size:3rem; font-weight:800; color:#1E3A8A; margin-bottom:0.25rem;">🎓 EduTrack AI</h1>
        <p style="color:#6B7280; font-size:1.1rem;">Seu assistente de gestão acadêmica inteligente</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_form, col_right = st.columns([1, 2, 1])
    with col_form:
        auth_mode = st.radio("", ["🔐 Entrar (Login)", "📝 Criar Conta"], horizontal=True, label_visibility="collapsed")
        st.markdown("---")

        if "🔐" in auth_mode:
            with st.form("login_form"):
                email = st.text_input("E-mail", placeholder="seu-email@exemplo.com")
                password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
                submitted = st.form_submit_button("Entrar no Sistema", use_container_width=True)

                if submitted:
                    if email and password:
                        try:
                            response = requests.post(f"{XANO_WORKSPACE_URL}/auth/login", json={"email": email, "password": password})
                            if response.status_code == 200:
                                data = response.json()
                                st.session_state['auth_token'] = data.get('authToken')
                                st.success("🎉 Login realizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("❌ Credenciais inválidas.")
                        except Exception as e:
                            st.error(f"❌ Erro de conexão: {e}")
                    else:
                        st.error("⚠️ Preencha todos os campos.")

            with st.expander("🔑 Esqueceu sua senha?"):
                reset_email = st.text_input("E-mail cadastrado", key="reset_em")
                if st.button("Solicitar Redefinição"):
                    if reset_email:
                        try:
                            r = requests.get(f"{XANO_WORKSPACE_URL}/reset/request-reset-link", params={"email": reset_email})
                            if r.status_code == 200:
                                st.success("✉️ E-mail de redefinição enviado!")
                            else:
                                st.error("❌ E-mail não encontrado.")
                        except Exception as e:
                            st.error(f"❌ Erro: {e}")
                    else:
                        st.error("⚠️ Digite seu e-mail.")
        else:
            with st.form("signup_form"):
                name_s = st.text_input("Nome Completo", placeholder="Ex: Maria Souza")
                email_s = st.text_input("E-mail", placeholder="seu-email@exemplo.com")
                password_s = st.text_input("Senha", type="password", placeholder="Mínimo 8 caracteres")
                submitted_s = st.form_submit_button("Criar Conta Acadêmica", use_container_width=True)

                if submitted_s:
                    if name_s and email_s and password_s:
                        if len(password_s) < 8:
                            st.error("⚠️ A senha deve ter pelo menos 8 caracteres.")
                        else:
                            try:
                                r = requests.post(f"{XANO_WORKSPACE_URL}/auth/signup", json={"name": name_s, "email": email_s, "password": password_s})
                                if r.status_code == 200:
                                    data = r.json()
                                    st.session_state['auth_token'] = data.get('authToken')
                                    st.success("🎉 Conta criada com sucesso!")
                                    st.rerun()
                                else:
                                    try:
                                        msg = r.json().get('message', 'Erro desconhecido.')
                                    except Exception:
                                        msg = 'Erro desconhecido.'
                                    st.error(f"❌ {msg}")
                            except Exception as e:
                                st.error(f"❌ Erro de conexão: {e}")
                    else:
                        st.error("⚠️ Preencha todos os campos.")

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD AUTENTICADO
# ══════════════════════════════════════════════════════════════════════════════
now = datetime.now()

# Buscar dados
user_data = make_xano_request('/auth/me') or {}
subjects  = make_xano_request('/subjects') or []
tasks     = make_xano_request('/academic_tasks') or []

user_name = user_data.get('name', 'Estudante')
hour = now.hour
greeting = "Bom dia" if hour < 12 else ("Boa tarde" if hour < 18 else "Boa noite")

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dashboard-hero">
    <p class="hero-title">🎓 {greeting}, {user_name.split()[0]}!</p>
    <p class="hero-sub">Aqui está seu resumo acadêmico para hoje, {now.strftime('%d de %B de %Y')}.</p>
</div>
""", unsafe_allow_html=True)

# ── Tela de boas-vindas para usuários sem dados ───────────────────────────────
if not subjects and not tasks:
    st.markdown("""
    <div class="welcome-empty">
        <h2>👋 Bem-vindo ao EduTrack AI!</h2>
        <p>Você ainda não tem disciplinas ou tarefas cadastradas.</p>
        <p>Use o menu lateral para começar adicionando suas <strong>disciplinas</strong> e depois suas <strong>tarefas</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Calcular métricas ─────────────────────────────────────────────────────────
total_subjects = len(subjects)
total_tasks    = len(tasks)
pending_tasks  = [t for t in tasks if t.get('status') == 'pending']
in_progress    = [t for t in tasks if t.get('status') == 'in_progress']
completed_tasks = [t for t in tasks if t.get('status') == 'completed']
completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0

PRIORITY_LABELS = {
    "low":    ("⬇️", "Baixa"),
    "medium": ("⏺️", "Média"),
    "high":   ("⬆️", "Alta"),
}

def safe_due(t):
    try:
        return datetime.fromisoformat(t['due_date'].split('T')[0])
    except Exception:
        return None

overdue_tasks = [
    t for t in tasks
    if t.get('status') != 'completed'
    and safe_due(t) is not None
    and safe_due(t) < now
]

upcoming_tasks = sorted(
    [
        t for t in tasks
        if t.get('status') != 'completed'
        and safe_due(t) is not None
        and safe_due(t) >= now
    ],
    key=lambda t: safe_due(t)
)[:5]

# ── Cartões de métricas ───────────────────────────────────────────────────────
mc1, mc2, mc3, mc4, mc5 = st.columns(5)

with mc1:
    st.metric("📚 Disciplinas", total_subjects)
with mc2:
    st.metric("📋 Total Tarefas", total_tasks)
with mc3:
    st.metric("⏳ Pendentes", len(pending_tasks))
with mc4:
    st.metric("⚠️ Atrasadas", len(overdue_tasks), delta=f"-{len(overdue_tasks)}" if overdue_tasks else None, delta_color="inverse")
with mc5:
    st.metric("✅ Progresso", f"{completion_rate:.1f}%")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Progresso geral ───────────────────────────────────────────────────────────
col_prog, col_next = st.columns([2, 3])

with col_prog:
    st.markdown('<p class="section-header">📈 Progresso Geral</p>', unsafe_allow_html=True)
    st.progress(completion_rate / 100)
    st.caption(f"{len(completed_tasks)} de {total_tasks} tarefas concluídas ({completion_rate:.1f}%)")

    if total_tasks > 0:
        c1, c2, c3 = st.columns(3)
        c1.metric("✅ Concluídas", len(completed_tasks))
        c2.metric("🔵 Em Andamento", len(in_progress))
        c3.metric("🟡 Pendentes", len(pending_tasks))

with col_next:
    st.markdown('<p class="section-header">📅 Próximas Tarefas</p>', unsafe_allow_html=True)
    subjects_map = {s['id']: s['name'] for s in subjects}

    if not upcoming_tasks:
        st.info("✅ Nenhuma tarefa pendente nos próximos dias!")
    else:
        for t in upcoming_tasks:
            due = safe_due(t)
            days_left = (due - now).days if due else None
            subj_name = subjects_map.get(t.get('subject_id'), 'N/A')
            priority = t.get('priority', 'medium')
            p_icon, _ = PRIORITY_LABELS.get(priority, ("⏺️", "Média"))

            is_today = days_left == 0
            card_cls = "today" if is_today else "task-card"

            if days_left == 0:
                days_txt = "📅 Vence hoje!"
            elif days_left == 1:
                days_txt = "⏰ Amanhã"
            else:
                days_txt = f"⏰ {days_left} dias"

            st.markdown(f"""
            <div class="task-card {'today' if is_today else ''}">
                <div class="task-title">{p_icon} {t.get('title', 'Sem título')}</div>
                <div class="task-meta">📚 {subj_name} &nbsp;·&nbsp; {days_txt} &nbsp;·&nbsp; {due.strftime('%d/%m/%Y') if due else ''}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Tarefas em Atraso ─────────────────────────────────────────────────────────
if overdue_tasks:
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">🚨 Tarefas em Atraso</p>', unsafe_allow_html=True)

    for t in sorted(overdue_tasks, key=lambda x: safe_due(x) or now):
        due = safe_due(t)
        days_ago = (now - due).days if due else 0
        subj_name = subjects_map.get(t.get('subject_id'), 'N/A')
        priority = t.get('priority', 'medium')
        p_icon, _ = PRIORITY_LABELS.get(priority, ("⏺️", "Média"))

        st.markdown(f"""
        <div class="task-card overdue">
            <div class="task-title">🔴 {p_icon} {t.get('title', 'Sem título')}</div>
            <div class="task-meta">📚 {subj_name} &nbsp;·&nbsp; ⚠️ Atrasada há {days_ago} dia(s) &nbsp;·&nbsp; Prazo: {due.strftime('%d/%m/%Y') if due else '—'}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Progresso por disciplina ──────────────────────────────────────────────────
if subjects:
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">📚 Progresso por Disciplina</p>', unsafe_allow_html=True)

    for subject in subjects:
        sid = subject.get('id')
        s_tasks = [t for t in tasks if t.get('subject_id') == sid]
        if not s_tasks:
            continue

        s_done  = len([t for t in s_tasks if t.get('status') == 'completed'])
        s_total = len(s_tasks)
        s_rate  = s_done / s_total if s_total > 0 else 0
        s_over  = [t for t in s_tasks if t.get('status') != 'completed' and safe_due(t) and safe_due(t) < now]

        col_subj, col_bar, col_pct = st.columns([2, 5, 1])
        with col_subj:
            overdue_badge = " 🚨" if s_over else ""
            st.markdown(f"**{subject.get('name')}{overdue_badge}**")
            st.caption(f"👨‍🏫 {subject.get('professor', 'N/A')}")
        with col_bar:
            st.markdown("<br>", unsafe_allow_html=True)
            st.progress(s_rate)
        with col_pct:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**{s_rate*100:.0f}%**")