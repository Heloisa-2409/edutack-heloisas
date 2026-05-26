import os
from dotenv import load_dotenv

load_dotenv()

XANO_BASE = os.getenv('XANO_BASE_URL', 'https://x8ki-letl-twmt.n7.xano.io').strip()

XANO_AUTH_URL     = f"{XANO_BASE}/api:VO5W-5oS"
XANO_SUBJECTS_URL = f"{XANO_BASE}/api:oSXUIWA9"
XANO_TASKS_URL    = f"{XANO_BASE}/api:jG_kIDdC"
XANO_MEMBERS_URL  = f"{XANO_BASE}/api:Ov46qsZP"

# Mantido para compatibilidade com código legado
XANO_WORKSPACE_URL = XANO_AUTH_URL
XANO_WORKSPACE_URL_IS_DEFAULT = False
XANO_WORKSPACE_URL_WARNING = None
