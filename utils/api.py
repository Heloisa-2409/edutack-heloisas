import streamlit as st
import requests
from utils.config import XANO_AUTH_URL, XANO_SUBJECTS_URL, XANO_TASKS_URL, XANO_MEMBERS_URL


def _base_url(endpoint: str) -> str:
    if endpoint.startswith('/subjects'):
        return XANO_SUBJECTS_URL
    if endpoint.startswith('/academic_tasks'):
        return XANO_TASKS_URL
    if endpoint.startswith(('/user/', '/account/', '/admin/')):
        return XANO_MEMBERS_URL
    return XANO_AUTH_URL


def make_xano_request(endpoint, method='GET', data=None, headers=None):
    """Faz uma requisição para a API Xano com tratamento de erro aprimorado."""
    url = f"{_base_url(endpoint)}{endpoint}"
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

        response.raise_for_status()

        if response.status_code == 204:
            return {"status": "success"}

        result = response.json()
        if isinstance(result, dict) and 'items' in result:
            return result['items']
        return result

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 401:
            st.session_state.pop('auth_token', None)
            st.session_state.pop('user', None)
            st.warning("⏱️ Sessão expirada. Faça login novamente.")
            st.switch_page("pages/0_🔐_Login.py")
        try:
            error_details = err.response.json()
            msg = error_details.get('message') or str(error_details)
            st.error(f"Erro da API (código {err.response.status_code}): {msg}\n\nURL: {err.response.url}")
        except ValueError:
            st.error(f"Erro na API (código {err.response.status_code}): {err.response.text}\n\nURL: {err.response.url}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: {e}")
        return None
