import streamlit as st
import requests
import os

XANO_WORKSPACE_URL = os.getenv('XANO_WORKSPACE_URL', 'https://x8ki-letl-twmt.xano.io/api')

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