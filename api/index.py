"""Vercel's entry point: exposes the FastAPI app as a Python function (openspec/changes/add-preview-deploy).

Vercel sends /api/* here (vercel.json) and serves the React build from its CDN. The bundle keeps the repo's layout
(src/rain_in_my_head/..., data/public.db), so config.ROOT resolves the same way as on the Mac. LISTENING_HOSTED,
DATABASE_URL and SESSION_SECRET come from the Vercel project's environment variables, declared in infra/.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("LISTENING_DB", str(ROOT / "data" / "public.db"))  # the two-year copy, never listening.db

from rain_in_my_head.api import app  # noqa: E402, F401  (Vercel looks for `app`)
