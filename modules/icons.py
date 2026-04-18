"""
Lucide icon library for the Drachmann Trading dashboard.
Every function returns an inline SVG string safe for st.markdown(unsafe_allow_html=True).
"""


def _svg(paths: str, size: int = 16, color: str = "currentColor",
         sw: float = 1.75, extra: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="display:inline-block;vertical-align:middle;{extra}">'
        f'{paths}</svg>'
    )


# ── Navigation ────────────────────────────────────────────────────────────────

def bar_chart(size=18, color="currentColor"):
    return _svg(
        '<line x1="18" y1="20" x2="18" y2="10"/>'
        '<line x1="12" y1="20" x2="12" y2="4"/>'
        '<line x1="6" y1="20" x2="6" y2="14"/>',
        size, color)

def search(size=18, color="currentColor"):
    return _svg(
        '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>',
        size, color)

def radio_tower(size=18, color="currentColor"):
    return _svg(
        '<path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9"/>'
        '<path d="M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5"/>'
        '<circle cx="12" cy="12" r="2"/>'
        '<path d="M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5"/>'
        '<path d="M19.1 4.9C23 8.8 23 15.1 19.1 19"/>',
        size, color)

def settings_gear(size=18, color="currentColor"):
    return _svg(
        '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 '
        '0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 '
        '2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 '
        '2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 '
        '1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15'
        '-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 '
        '0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>'
        '<circle cx="12" cy="12" r="3"/>',
        size, color)


# ── Signals ───────────────────────────────────────────────────────────────────

def zap(size=14, color="#22c55e"):
    return _svg('<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>', size, color, 1.5)

def trending_up(size=14, color="#86efac"):
    return _svg(
        '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
        '<polyline points="16 7 22 7 22 13"/>',
        size, color)

def minus_icon(size=14, color="#f59e0b"):
    return _svg('<line x1="5" y1="12" x2="19" y2="12"/>', size, color, 2.25)

def trending_down(size=14, color="#ef4444"):
    return _svg(
        '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/>'
        '<polyline points="16 17 22 17 22 11"/>',
        size, color)


# ── Actions ───────────────────────────────────────────────────────────────────

def refresh_cw(size=15, color="currentColor"):
    return _svg(
        '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>'
        '<path d="M21 3v5h-5"/>'
        '<path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>'
        '<path d="M8 16H3v5"/>',
        size, color)

def send_icon(size=15, color="currentColor"):
    return _svg(
        '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
        size, color)

def flask_icon(size=15, color="currentColor"):
    return _svg(
        '<path d="M10 2v7.31"/><path d="M14 9.3V1.99"/>'
        '<path d="M8.5 2h7"/>'
        '<path d="M14 9.3a6.5 6.5 0 1 1-4 0"/>',
        size, color)

def check_circle(size=14, color="#22c55e"):
    return _svg(
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
        '<polyline points="22 4 12 14.01 9 11.01"/>',
        size, color)

def x_circle(size=14, color="#ef4444"):
    return _svg(
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="15" y1="9" x2="9" y2="15"/>'
        '<line x1="9" y1="9" x2="15" y2="15"/>',
        size, color)

def clock_icon(size=14, color="currentColor"):
    return _svg(
        '<circle cx="12" cy="12" r="10"/>'
        '<polyline points="12 6 12 12 16 14"/>',
        size, color)

def mail_icon(size=14, color="currentColor"):
    return _svg(
        '<rect width="20" height="16" x="2" y="4" rx="2"/>'
        '<path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
        size, color)


# ── KPI / General ─────────────────────────────────────────────────────────────

def target(size=18, color="currentColor"):
    return _svg(
        '<circle cx="12" cy="12" r="10"/>'
        '<circle cx="12" cy="12" r="6"/>'
        '<circle cx="12" cy="12" r="2"/>',
        size, color)

def activity(size=18, color="currentColor"):
    return _svg(
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
        size, color)

def award(size=18, color="currentColor"):
    return _svg(
        '<circle cx="12" cy="8" r="6"/>'
        '<path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
        size, color)

def layers(size=18, color="currentColor"):
    return _svg(
        '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 '
        '1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/>'
        '<path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/>'
        '<path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
        size, color)

def info_icon(size=16, color="currentColor"):
    return _svg(
        '<circle cx="12" cy="12" r="10"/>'
        '<path d="M12 16v-4"/><path d="M12 8h.01"/>',
        size, color)


# ── Compound helpers ──────────────────────────────────────────────────────────

def signal_icon(signal: str, size: int = 14) -> str:
    return {
        "STRONG BUY": zap(size, "#22c55e"),
        "BUY":        trending_up(size, "#86efac"),
        "HOLD":       minus_icon(size, "#f59e0b"),
        "SELL":       trending_down(size, "#ef4444"),
    }.get(signal or "", "")


def signal_badge(signal: str) -> str:
    """Colored HTML pill with Lucide icon for a signal string."""
    palette = {
        "STRONG BUY": ("rgba(34,197,94,0.12)",  "rgba(34,197,94,0.35)",   "#22c55e"),
        "BUY":        ("rgba(134,239,172,0.10)", "rgba(134,239,172,0.30)", "#86efac"),
        "HOLD":       ("rgba(245,158,11,0.10)",  "rgba(245,158,11,0.30)",  "#f59e0b"),
        "SELL":       ("rgba(239,68,68,0.10)",   "rgba(239,68,68,0.30)",   "#ef4444"),
    }
    bg, border, color = palette.get(signal or "", ("rgba(148,163,184,0.1)", "rgba(148,163,184,0.3)", "#94a3b8"))
    ico = signal_icon(signal, 12)
    label = signal or "—"
    return (
        f'<span style="display:inline-flex;align-items:center;gap:5px;'
        f'padding:4px 11px;border-radius:20px;font-size:11px;font-weight:600;'
        f'letter-spacing:0.06em;color:{color};background:{bg};border:1px solid {border};">'
        f'{ico}{label}</span>'
    )


def page_header(icon_svg: str, title: str, subtitle: str = "") -> str:
    """Styled page header with an icon."""
    sub = f'<p style="color:#64748b;font-size:13px;margin:4px 0 0;">{subtitle}</p>' if subtitle else ""
    return (
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
        f'<div style="padding:10px;background:rgba(59,130,246,0.12);border-radius:10px;'
        f'border:1px solid rgba(59,130,246,0.2);">{icon_svg}</div>'
        f'<div><h1 style="margin:0;font-size:26px;font-weight:700;color:#f1f5f9;">'
        f'{title}</h1>{sub}</div></div>'
    )
