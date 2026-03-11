import streamlit as st
import requests
import json
import time
import uuid
import html as html_mod
import re
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
#  PAGE CONFIG  (must be very first Streamlit call)
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NeuralChat · Ollama",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
#  SESSION STATE BOOTSTRAP
# ═══════════════════════════════════════════════════════════════
if "theme"          not in st.session_state: st.session_state.theme          = "dark"
if "chat_sessions"  not in st.session_state: st.session_state.chat_sessions  = {}
if "active_session" not in st.session_state: st.session_state.active_session = None
if "input_key"      not in st.session_state: st.session_state.input_key      = 0

# ═══════════════════════════════════════════════════════════════
#  THEME TOKENS
# ═══════════════════════════════════════════════════════════════
THEMES = {
    "dark": dict(
        bg="#0e1117", surface="#161b27", surface2="#1c2235",
        border="#252d3d", border2="#2e3a52",
        text="#e8edf5", text2="#8899b4", text3="#445566",
        accent="#4f9cf9", accent2="#8b5cf6",
        accent_glow="rgba(79,156,249,0.16)",
        user_bg="linear-gradient(135deg,#1a2e50,#16213a)",
        user_border="#2a4a8c",
        ai_bg="#161b27", ai_border="#252d3d",
        danger="#ff4757", success="#2ed573", warn="#ffa502",
        input_bg="#111827", scrollbar="#252d3d",
    ),
    "light": dict(
        bg="#f0f4ff", surface="#ffffff", surface2="#eef2ff",
        border="#dde4f2", border2="#c8d3ec",
        text="#1a2240", text2="#5a6a8a", text3="#99a8c2",
        accent="#2563eb", accent2="#7c3aed",
        accent_glow="rgba(37,99,235,0.10)",
        user_bg="linear-gradient(135deg,#dbeafe,#ede9fe)",
        user_border="#93c5fd",
        ai_bg="#ffffff", ai_border="#dde4f2",
        danger="#ef4444", success="#16a34a", warn="#d97706",
        input_bg="#f8faff", scrollbar="#c8d3ec",
    ),
}
T = THEMES[st.session_state.theme]

# ═══════════════════════════════════════════════════════════════
#  INJECT CSS
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

:root{{
  --bg:{T['bg']}; --sf:{T['surface']}; --sf2:{T['surface2']};
  --bd:{T['border']}; --bd2:{T['border2']};
  --tx:{T['text']}; --tx2:{T['text2']}; --tx3:{T['text3']};
  --ac:{T['accent']}; --ac2:{T['accent2']}; --acg:{T['accent_glow']};
  --ubg:{T['user_bg']}; --ubd:{T['user_border']};
  --abg:{T['ai_bg']}; --abd:{T['ai_border']};
  --err:{T['danger']}; --ok:{T['success']}; --warn:{T['warn']};
  --inp:{T['input_bg']}; --scr:{T['scrollbar']};
  --r:14px; --rs:8px;
}}
*,*::before,*::after{{box-sizing:border-box}}
html,body,[class*="css"]{{font-family:'Outfit',sans-serif!important;background:var(--bg)!important;color:var(--tx)!important}}
::-webkit-scrollbar{{width:4px;height:4px}}
::-webkit-scrollbar-thumb{{background:var(--scr);border-radius:99px}}
#MainMenu,footer,header{{visibility:hidden!important}}
.block-container{{padding:1rem 1.6rem .8rem!important;max-width:100%!important}}

/* sidebar */
[data-testid="stSidebar"]{{background:var(--sf)!important;border-right:1px solid var(--bd)!important}}
[data-testid="stSidebar"] *{{color:var(--tx)!important}}
[data-testid="stSidebar"] .stMarkdown p{{color:var(--tx2)!important}}
.stApp{{background:var(--bg)!important}}

/* brand */
.brand-wrap{{display:flex;align-items:center;gap:10px;padding:4px 0 14px}}
.brand-icon{{width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,var(--ac),var(--ac2));display:flex;align-items:center;justify-content:center;font-size:1rem;box-shadow:0 0 18px var(--acg);flex-shrink:0}}
.brand-name{{font-size:1.2rem;font-weight:800;letter-spacing:-.02em;background:linear-gradient(135deg,var(--ac),var(--ac2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1}}
.brand-sub{{font-size:.65rem;color:var(--tx3);letter-spacing:.07em;text-transform:uppercase;font-weight:500}}
.slabel{{font-size:.67rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--tx3);margin:14px 0 7px}}

/* status */
.spill{{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:99px;font-size:.72rem;font-weight:600}}
.spill.on{{background:rgba(46,213,115,.1);color:var(--ok);border:1px solid rgba(46,213,115,.25)}}
.spill.off{{background:rgba(255,71,87,.1);color:var(--err);border:1px solid rgba(255,71,87,.25)}}
.pdot{{width:6px;height:6px;border-radius:50%}}
.pdot.on{{background:var(--ok);animation:pg 1.5s infinite}}
.pdot.off{{background:var(--err)}}
@keyframes pg{{0%,100%{{box-shadow:0 0 0 0 rgba(46,213,115,.4)}}50%{{box-shadow:0 0 0 4px transparent}}}}

/* session cards */
.sc{{padding:9px 12px;border-radius:var(--rs);border:1px solid var(--bd);background:var(--sf2);margin-bottom:4px}}
.sc.act{{border-color:var(--ac);background:var(--acg);box-shadow:0 0 0 1px var(--ac)}}
.sc-title{{font-size:.82rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.sc-meta{{font-size:.67rem;color:var(--tx3);margin-top:2px}}

/* buttons */
.stButton>button{{background:linear-gradient(135deg,var(--ac),var(--ac2))!important;color:#fff!important;border:none!important;border-radius:var(--rs)!important;font-family:'Outfit',sans-serif!important;font-weight:600!important;font-size:.84rem!important;padding:.42rem .9rem!important;transition:all .18s ease!important;box-shadow:0 2px 12px var(--acg)!important}}
.stButton>button:hover{{transform:translateY(-1px)!important;opacity:.9!important}}
[data-testid="stDownloadButton"]>button{{background:var(--sf2)!important;color:var(--tx2)!important;border:1px solid var(--bd)!important;box-shadow:none!important}}
[data-testid="stDownloadButton"]>button:hover{{border-color:var(--ac)!important;color:var(--ac)!important}}

/* inputs */
.stTextArea textarea,.stTextInput input{{background:var(--inp)!important;color:var(--tx)!important;border:1.5px solid var(--bd)!important;border-radius:var(--rs)!important;font-family:'Outfit',sans-serif!important;font-size:.9rem!important;transition:border .18s!important}}
.stTextArea textarea:focus,.stTextInput input:focus{{border-color:var(--ac)!important;box-shadow:0 0 0 3px var(--acg)!important}}
label{{color:var(--tx2)!important;font-size:.78rem!important;font-weight:500!important}}
.stSelectbox>div>div{{background:var(--inp)!important;border:1.5px solid var(--bd)!important;color:var(--tx)!important;border-radius:var(--rs)!important}}
.stSelectbox [data-baseweb="select"] span{{color:var(--tx)!important}}
.stSlider>div>div>div>div{{background:var(--ac)!important}}
.stSlider>div>div>div{{background:var(--bd)!important}}

/* metrics */
[data-testid="stMetric"]{{background:var(--sf2)!important;border:1px solid var(--bd)!important;border-radius:var(--rs)!important;padding:9px 12px!important}}
[data-testid="stMetricValue"]{{color:var(--ac)!important;font-weight:700!important}}
[data-testid="stMetricLabel"]{{color:var(--tx3)!important;font-size:.68rem!important}}
hr{{border-color:var(--bd)!important;margin:8px 0!important}}
.stSpinner>div{{border-top-color:var(--ac)!important}}

/* top bar */
.topbar{{display:flex;align-items:center;justify-content:space-between;padding-bottom:12px;border-bottom:1px solid var(--bd);margin-bottom:12px}}
.topbar-left{{display:flex;align-items:center;gap:10px}}
.sname{{font-size:1.05rem;font-weight:700;letter-spacing:-.01em}}
.mtag{{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:99px;background:var(--sf2);border:1px solid var(--bd2);font-size:.7rem;font-weight:600;color:var(--tx2);font-family:'Fira Code',monospace}}

/* chat viewport */
.chat-vp{{height:60vh;overflow-y:auto;padding:8px 2px 4px;display:flex;flex-direction:column;gap:2px}}

/* messages */
.mrow{{display:flex;gap:10px;animation:su .2s ease both;padding:3px 2px}}
.mrow.user{{flex-direction:row-reverse}}
@keyframes su{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
.av{{width:32px;height:32px;border-radius:9px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:700;margin-top:4px}}
.av.user{{background:linear-gradient(135deg,var(--ac),var(--ac2));color:#fff}}
.av.ai{{background:var(--sf2);border:1px solid var(--bd2);color:var(--tx2)}}
.bwrap{{max-width:74%;display:flex;flex-direction:column}}
.mrow.user .bwrap{{align-items:flex-end}}
.bbl{{padding:10px 14px;border-radius:var(--r);line-height:1.65;font-size:.9rem;word-wrap:break-word;position:relative}}
.bbl.user{{background:var(--ubg);border:1px solid var(--ubd);color:var(--tx);border-bottom-right-radius:4px}}
.bbl.ai{{background:var(--abg);border:1px solid var(--abd);color:var(--tx);border-bottom-left-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
.bbl code{{font-family:'Fira Code',monospace;font-size:.8rem;background:var(--sf2);padding:2px 5px;border-radius:4px;color:var(--ac)}}
.bbl pre{{background:var(--sf2)!important;border:1px solid var(--bd)!important;border-radius:var(--rs)!important;padding:10px!important;overflow-x:auto!important;margin:7px 0 0!important}}
.bbl pre code{{background:none!important;padding:0!important;font-size:.8rem!important}}
.bmeta{{font-size:.63rem;color:var(--tx3);margin-top:3px;display:flex;gap:7px;align-items:center}}

/* typing */
.tdots{{display:flex;align-items:center;gap:4px;padding:11px 15px;background:var(--abg);border:1px solid var(--abd);border-radius:var(--r);border-bottom-left-radius:4px;width:fit-content;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
.td{{width:6px;height:6px;border-radius:50%;background:var(--tx3);animation:bn 1.2s infinite}}
.td:nth-child(2){{animation-delay:.2s}}
.td:nth-child(3){{animation-delay:.4s}}
@keyframes bn{{0%,80%,100%{{transform:translateY(0);opacity:.4}}40%{{transform:translateY(-5px);opacity:1}}}}

/* empty state */
.estate{{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:14px;padding:2.5rem;text-align:center}}
.eicon{{width:60px;height:60px;border-radius:16px;background:linear-gradient(135deg,var(--ac),var(--ac2));display:flex;align-items:center;justify-content:center;font-size:1.6rem;box-shadow:0 8px 26px var(--acg);animation:fl 3s ease-in-out infinite}}
@keyframes fl{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
.etitle{{font-size:1.1rem;font-weight:700}}
.esub{{font-size:.8rem;color:var(--tx3);max-width:270px;line-height:1.65}}
.qp{{display:inline-block;padding:5px 13px;border:1px solid var(--bd2);border-radius:99px;font-size:.76rem;color:var(--tx2);background:var(--sf2);margin:3px;cursor:pointer;transition:all .14s}}
.qp:hover{{border-color:var(--ac);color:var(--ac);background:var(--acg)}}

/* input bar */
.ibar{{border-top:1px solid var(--bd);padding-top:10px;margin-top:4px}}
.cctr{{font-size:.65rem;color:var(--tx3);text-align:right;margin-top:2px}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  CONSTANTS & HELPERS
# ═══════════════════════════════════════════════════════════════
OLLAMA_BASE = "http://localhost:11434"
API_CHAT    = f"{OLLAMA_BASE}/api/chat"
API_TAGS    = f"{OLLAMA_BASE}/api/tags"

QUICK_PROMPTS = [
    "✨ Explain like I'm 5", "🐍 Write Python code",
    "📋 Summarize this",     "⚖️ Compare pros & cons",
    "💡 Give me ideas",      "🐛 Debug my code",
]

def check_ollama():
    try: return requests.get(OLLAMA_BASE, timeout=2).status_code == 200
    except: return False

def get_models():
    try:
        r = requests.get(API_TAGS, timeout=3)
        if r.status_code == 200:
            return [m["name"] for m in r.json().get("models", [])]
    except: pass
    return []

def new_session(model="llama3.2"):
    sid = str(uuid.uuid4())[:8]
    st.session_state.chat_sessions[sid] = {
        "title": f"Chat {datetime.now().strftime('%b %d, %H:%M')}",
        "messages": [], "model": model,
        "created_at": datetime.now().isoformat(),
        "response_times": [],
    }
    st.session_state.active_session = sid
    return sid

def get_active():
    sid = st.session_state.active_session
    return st.session_state.chat_sessions.get(sid) if sid else None

def stream_ollama(model, messages, temperature, system_prompt):
    payload_msgs = []
    if system_prompt.strip():
        payload_msgs.append({"role": "system", "content": system_prompt})
    payload_msgs.extend(messages)
    payload = {"model": model, "messages": payload_msgs, "stream": True,
               "options": {"temperature": temperature}}
    start = time.time()
    try:
        with requests.post(API_CHAT, json=payload, stream=True, timeout=180) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line.decode())
                    token = chunk.get("message", {}).get("content", "")
                    yield token, False, None
                    if chunk.get("done"):
                        yield "", True, round(time.time() - start, 2)
    except requests.exceptions.ConnectionError:
        yield "⚠️ Cannot connect to Ollama — run `ollama serve`", True, None
    except Exception as e:
        yield f"⚠️ Error: {e}", True, None

def auto_title(text):
    words = text.strip().split()[:7]
    t = " ".join(words)
    return (t[:36] + "…") if len(t) > 36 else t

def fmt_time(iso):
    try: return datetime.fromisoformat(iso).strftime("%b %d · %H:%M")
    except: return ""

def wc(text): return len(text.split())

def render_content(text):
    """Escape HTML then lightly format for display."""
    s = html_mod.escape(text)
    s = s.replace("\n", "<br>")
    s = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', s)
    return s

# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="brand-wrap">
      <div class="brand-icon">⚡</div>
      <div>
        <div class="brand-name">NeuralChat</div>
        <div class="brand-sub">Local AI · Powered by Ollama</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Theme ──
    st.markdown('<div class="slabel">🎨 Appearance</div>', unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    with tc1:
        if st.button("🌙 Dark", use_container_width=True,
                     type="primary" if st.session_state.theme=="dark" else "secondary"):
            st.session_state.theme = "dark"; st.rerun()
    with tc2:
        if st.button("☀️ Light", use_container_width=True,
                     type="primary" if st.session_state.theme=="light" else "secondary"):
            st.session_state.theme = "light"; st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Status ──
    is_online = check_ollama()
    sc, sl = ("on","Ollama Connected") if is_online else ("off","Ollama Offline")
    st.markdown(f'<div class="spill {sc}"><div class="pdot {sc}"></div>{sl}</div>',
                unsafe_allow_html=True)
    if not is_online:
        st.caption("Run `ollama serve` to connect")
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Model settings ──
    st.markdown('<div class="slabel">⚙️ Model Settings</div>', unsafe_allow_html=True)
    models = get_models()
    if models:
        selected_model = st.selectbox("Model", models, label_visibility="collapsed")
    else:
        selected_model = st.text_input("Model", "llama3.2",
                                       label_visibility="collapsed",
                                       placeholder="e.g. llama3.2, mistral…")

    temperature = st.slider("🌡️ Temperature", 0.0, 2.0, 0.72, 0.01)
    max_tokens  = st.slider("📏 Max Tokens", 256, 4096, 1024, 64)

    system_prompt = st.text_area(
        "System Prompt", height=80, label_visibility="collapsed",
        value="You are a brilliant, concise AI assistant. Give clear and accurate answers. Use code blocks when writing code.",
        placeholder="System instruction…",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Chat History ──
    st.markdown('<div class="slabel">📂 Chat History</div>', unsafe_allow_html=True)

    if st.button("＋  New Chat", use_container_width=True):
        new_session(selected_model); st.rerun()

    sessions = st.session_state.chat_sessions
    if sessions:
        sorted_sids = sorted(sessions, key=lambda s: sessions[s]["created_at"], reverse=True)
        for sid in sorted_sids:
            sess_item = sessions[sid]
            active    = (sid == st.session_state.active_session)
            card_cls  = "sc act" if active else "sc"
            n_user    = len([m for m in sess_item["messages"] if m["role"]=="user"])
            meta_str  = f"{fmt_time(sess_item['created_at'])} · {n_user} msg{'s' if n_user!=1 else ''}"

            st.markdown(f"""
            <div class="{card_cls}">
              <div class="sc-title">{sess_item['title']}</div>
              <div class="sc-meta">{meta_str}</div>
            </div>""", unsafe_allow_html=True)

            oc1, oc2 = st.columns([5, 1])
            with oc1:
                if st.button("Open", key=f"open_{sid}", use_container_width=True):
                    st.session_state.active_session = sid; st.rerun()
            with oc2:
                if st.button("🗑", key=f"del_{sid}", help="Delete"):
                    del st.session_state.chat_sessions[sid]
                    remaining = list(st.session_state.chat_sessions.keys())
                    st.session_state.active_session = remaining[0] if remaining else None
                    st.rerun()
    else:
        st.markdown('<div style="color:var(--tx3);font-size:.77rem;padding:6px 0">No chats yet.</div>',
                    unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Stats for active session ──
    sess = get_active()
    if sess and sess["messages"]:
        n_u  = len([m for m in sess["messages"] if m["role"]=="user"])
        rt   = sess["response_times"]
        avg  = round(sum(rt)/len(rt),1) if rt else 0
        twds = sum(wc(m["content"]) for m in sess["messages"])
        c1,c2,c3 = st.columns(3)
        c1.metric("💬",n_u)
        c2.metric("⚡",f"{avg}s")
        c3.metric("📝",twds)

        chat_txt = "\n\n".join(
            f"[{m['role'].upper()} {m.get('ts','')}]\n{m['content']}"
            for m in sess["messages"]
        )
        safe_title = re.sub(r'[^a-zA-Z0-9_\-]','_', sess['title'])[:20]
        st.download_button("💾 Export Chat", data=chat_txt,
                           file_name=f"neuralchat_{safe_title}.txt",
                           mime="text/plain", use_container_width=True)

    st.markdown("""
    <div style="margin-top:14px;font-size:.63rem;color:var(--tx3);text-align:center;line-height:1.9">
      NeuralChat · localhost:11434<br><span style="opacity:.45">runs 100% on your machine</span>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  ENSURE ACTIVE SESSION
# ═══════════════════════════════════════════════════════════════
if (st.session_state.active_session is None or
        st.session_state.active_session not in st.session_state.chat_sessions):
    new_session(selected_model)

sess = get_active()

# ═══════════════════════════════════════════════════════════════
#  TOP BAR
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <div class="sname">{sess['title']}</div>
    <div class="mtag">⚡ {sess.get('model', selected_model)}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  CHAT VIEWPORT
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="chat-vp" id="chat-vp">', unsafe_allow_html=True)

if not sess["messages"]:
    prompts_html = "".join(f'<span class="qp">{p}</span>' for p in QUICK_PROMPTS)
    st.markdown(f"""
    <div class="estate">
      <div class="eicon">⚡</div>
      <div class="etitle">Start a conversation</div>
      <div class="esub">Ask anything — your AI runs privately on your local machine via Ollama.</div>
      <div style="margin-top:8px">{prompts_html}</div>
    </div>""", unsafe_allow_html=True)
else:
    for msg in sess["messages"]:
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("ts","")
        rt      = msg.get("response_time","")
        rendered = render_content(content)

        if role == "user":
            st.markdown(f"""
            <div class="mrow user">
              <div class="av user">U</div>
              <div class="bwrap">
                <div class="bbl user">{rendered}</div>
                <div class="bmeta" style="justify-content:flex-end">
                  <span>{ts}</span>
                  <span>📝 {wc(content)}w</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            m_short = (sess.get("model","AI")[:2]).upper()
            rt_html = f"<span>⚡ {rt}s</span>" if rt else ""
            st.markdown(f"""
            <div class="mrow assistant">
              <div class="av ai">{m_short}</div>
              <div class="bwrap">
                <div class="bbl ai">{rendered}</div>
                <div class="bmeta">
                  <span>{ts}</span>{rt_html}
                  <span>📝 {wc(content)}w</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Auto-scroll
st.markdown("""
<script>
(function(){
  const vp = document.getElementById('chat-vp');
  if(vp) vp.scrollTop = vp.scrollHeight;
  const obs = new MutationObserver(()=>{ if(vp) vp.scrollTop = vp.scrollHeight; });
  if(vp) obs.observe(vp, {childList:true, subtree:true});
})();
</script>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  INPUT BAR
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="ibar">', unsafe_allow_html=True)
ci, cb = st.columns([6, 1])
with ci:
    user_input = st.text_area(
        "msg", label_visibility="collapsed",
        key=f"inp_{st.session_state.input_key}",
        placeholder="Message NeuralChat…  (Shift+Enter for new line)",
        height=70,
    )
    char_n = len(user_input) if user_input else 0
    st.markdown(f'<div class="cctr">{char_n} / 4000</div>', unsafe_allow_html=True)
with cb:
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    send_btn = st.button("Send ➤", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  SEND HANDLER
# ═══════════════════════════════════════════════════════════════
if send_btn and user_input and user_input.strip():
    if not is_online:
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        st.stop()

    text   = user_input.strip()
    now_ts = datetime.now().strftime("%H:%M")

    # Auto-title on first message
    if not sess["messages"]:
        sess["title"] = auto_title(text)
        sess["model"] = selected_model

    sess["messages"].append({"role": "user", "content": text, "ts": now_ts})
    st.session_state.input_key += 1

    # Typing indicator
    placeholder = st.empty()
    placeholder.markdown("""
    <div class="mrow assistant" style="padding:3px 2px">
      <div class="av ai">AI</div>
      <div class="tdots">
        <div class="td"></div><div class="td"></div><div class="td"></div>
      </div>
    </div>""", unsafe_allow_html=True)

    full_resp = ""
    elapsed   = None
    m_short   = (selected_model[:2]).upper()

    history_payload = [{"role": m["role"], "content": m["content"]} for m in sess["messages"]]

    for token, done, t in stream_ollama(
        model=selected_model,
        messages=history_payload,
        temperature=temperature,
        system_prompt=system_prompt,
    ):
        if not done:
            full_resp += token
            rendered_live = render_content(full_resp)
            placeholder.markdown(f"""
            <div class="mrow assistant" style="padding:3px 2px">
              <div class="av ai">{m_short}</div>
              <div class="bwrap">
                <div class="bbl ai">{rendered_live}<span style="opacity:.5;animation:bn 1s infinite">▌</span></div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            elapsed = t
            placeholder.empty()

    if full_resp:
        sess["messages"].append({
            "role": "assistant", "content": full_resp,
            "ts": datetime.now().strftime("%H:%M"),
            "response_time": elapsed,
        })
        if elapsed:
            sess["response_times"].append(elapsed)

    st.rerun()