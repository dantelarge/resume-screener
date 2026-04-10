# -*- coding: utf-8 -*-
import os
import io
import json
import streamlit as st
import anthropic
import PyPDF2
import docx
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Resume Screener AI", page_icon="🎯", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg:         #09080a;
    --bg-2:       #100e14;
    --bg-3:       #161220;
    --border:     #211d2e;
    --border-2:   #2e2940;
    --amber:      #d4a853;
    --amber-dim:  #a07a34;
    --amber-glow: rgba(212,168,83,0.12);
    --amber-ring: rgba(212,168,83,0.25);
    --text-1:     #f0ece4;
    --text-2:     #9b9192;
    --text-3:     #5c5460;
    --green:      #5ebd8a;
    --green-dim:  rgba(94,189,138,0.08);
    --red:        #c97070;
    --red-dim:    rgba(201,112,112,0.08);
    --blue:       #7b8fcf;
    --blue-dim:   rgba(123,143,207,0.08);
}

* { box-sizing: border-box; }

.stApp {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: var(--bg);
    color: var(--text-1);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 2.5rem 4rem 2.5rem !important; max-width: 1320px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg-2); }
::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 4px; }

/* ── Navbar ── */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 1.75rem;
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-top: 2px solid var(--amber);
    border-radius: 0 0 14px 14px;
    margin-bottom: 4rem;
}
.nav-wordmark {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.55rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: var(--text-1);
    text-transform: uppercase;
}
.nav-wordmark em {
    font-style: italic;
    color: var(--amber);
}
.nav-sub {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-top: 2px;
}
.nav-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-3);
    border: 1px solid var(--border-2);
    padding: 7px 16px;
    border-radius: 3px;
}
.nav-badge-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 7px rgba(94,189,138,0.7);
    animation: pulse 2.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 0 0 4rem 0;
    position: relative;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--amber);
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
}
.hero-eyebrow::before, .hero-eyebrow::after {
    content: '';
    display: block;
    width: 48px;
    height: 1px;
    background: var(--amber-dim);
}
.hero h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 4.8rem;
    font-weight: 300;
    font-style: italic;
    color: var(--text-1);
    letter-spacing: -0.5px;
    margin: 0 0 1.5rem 0;
    line-height: 1.0;
}
.hero h1 strong {
    font-weight: 700;
    font-style: normal;
    color: var(--amber);
}
.hero-sub {
    font-size: 0.95rem;
    font-weight: 400;
    color: var(--text-2);
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.8;
}
.hero-rule {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-top: 2.5rem;
}
.hero-rule-line { flex: 1; max-width: 100px; height: 1px; background: var(--border-2); }
.hero-rule-diamond {
    width: 7px; height: 7px;
    background: var(--amber);
    transform: rotate(45deg);
    opacity: 0.7;
}

/* ── Input cards ── */
.input-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--amber-dim);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.input-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Streamlit widget overrides ── */
.stTextArea textarea {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-left: 2px solid var(--border-2) !important;
    border-radius: 6px !important;
    color: var(--text-1) !important;
    font-size: 0.88rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    line-height: 1.7 !important;
}
.stTextArea textarea:focus {
    border-color: var(--border-2) !important;
    border-left-color: var(--amber) !important;
    box-shadow: none !important;
}
.stFileUploader {
    background: var(--bg-2) !important;
    border: 1px dashed var(--border-2) !important;
    border-radius: 6px !important;
}
[data-testid="stFileUploaderDropzone"] { background: var(--bg-2) !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--amber-dim) !important; }

/* ── Analyze button ── */
.stButton > button {
    background: transparent !important;
    color: var(--amber) !important;
    border: 1px solid var(--amber-dim) !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 0.8rem 2rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--amber-glow) !important;
    border-color: var(--amber) !important;
    box-shadow: 0 0 24px var(--amber-ring) !important;
}

/* ── Divider ── */
.divider { border: none; border-top: 1px solid var(--border); margin: 3rem 0; }

/* ── Results header ── */
.results-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 2rem;
}
.results-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-1);
    letter-spacing: -0.3px;
}
.results-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-3);
    letter-spacing: 0.1em;
}

/* ── Score card ── */
.score-card {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 32px 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    position: relative;
    overflow: hidden;
}
.score-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--amber), transparent);
    opacity: 0.6;
}
.score-ring-wrap { position: relative; width: 148px; height: 148px; }
.score-ring-wrap svg { transform: rotate(-90deg); }
.score-center {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    text-align: center;
}
.score-num {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.4rem;
    font-weight: 700;
    line-height: 1;
}
.score-denom {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: var(--text-3);
    letter-spacing: 0.1em;
    margin-top: 4px;
}
.score-bar-wrap { width: 100%; }
.score-bar-label {
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--text-3);
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}
.score-bar-track { background: var(--border); border-radius: 1px; height: 3px; }
.score-bar-fill { height: 100%; border-radius: 1px; }

/* ── Verdict card ── */
.verdict-card {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 28px 24px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.verdict-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--amber), transparent);
    opacity: 0.6;
}
.v-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: 8px;
}
.verdict-text {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.9rem;
    font-weight: 600;
    letter-spacing: -0.3px;
    line-height: 1.1;
}
.match-text {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.82rem;
    font-weight: 500;
}
.v-rule { border: none; border-top: 1px solid var(--border); margin: 0; }

/* ── Summary card ── */
.summary-card {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 28px 28px;
    height: 100%;
}
.summary-card p {
    font-size: 0.93rem;
    color: var(--text-2);
    line-height: 1.85;
    margin: 0;
}
.card-head {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.card-head::after { content: ''; flex: 1; height: 1px; background: var(--border); }

/* ── List cards ── */
.list-card {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 24px;
    height: 100%;
}
.list-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 11px 14px;
    border-radius: 6px;
    margin-bottom: 7px;
    font-size: 0.86rem;
    line-height: 1.65;
}
.list-item:last-child { margin-bottom: 0; }
.li-green { background: var(--green-dim); border-left: 2px solid var(--green); color: #a8d8be; }
.li-red   { background: var(--red-dim);   border-left: 2px solid var(--red);   color: #d9a8a8; }
.li-blue  { background: var(--blue-dim);  border-left: 2px solid var(--blue);  color: #b0bcdf; }
.li-icon  {
    flex-shrink: 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    min-width: 20px;
    margin-top: 3px;
    letter-spacing: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li {
    color: var(--text-2) !important;
    font-size: 0.87rem !important;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--text-1) !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-1) !important;
    border-radius: 5px !important;
}
.sidebar-wordmark {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.3rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-1);
    padding: 4px 0 18px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
}
.sidebar-wordmark em { font-style: italic; color: var(--amber); }
.step-row { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 14px; }
.step-num {
    min-width: 20px; height: 20px;
    border: 1px solid var(--border-2);
    color: var(--amber-dim);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    border-radius: 3px;
    flex-shrink: 0;
}
.step-text { font-size: 0.85rem; color: var(--text-2); line-height: 1.5; padding-top: 1px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-wordmark">Résumé<em>·AI</em></div>
    """, unsafe_allow_html=True)

    env_key = os.getenv("ANTHROPIC_API_KEY", "")
    if env_key:
        api_key = env_key
        st.success("✅ API key loaded")
    else:
        api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        st.caption("Or add `ANTHROPIC_API_KEY` to `.env`")

    st.markdown("---")
    st.markdown("**How to use**")
    st.markdown("""
    <div class="step-row"><div class="step-num">1</div><div class="step-text">Paste the job description</div></div>
    <div class="step-row"><div class="step-num">2</div><div class="step-text">Upload a resume or paste text</div></div>
    <div class="step-row"><div class="step-num">3</div><div class="step-text">Hit Analyze Resume</div></div>
    <div class="step-row"><div class="step-num">4</div><div class="step-text">Review the AI report</div></div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Powered by Claude · Built with Streamlit")

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div>
        <div class="nav-wordmark">Résumé<em>·AI</em></div>
        <div class="nav-sub">Intelligent Candidate Screener</div>
    </div>
    <div class="nav-badge">
        <span class="nav-badge-dot"></span>
        Claude · Active
    </div>
</div>

<div class="hero">
    <div class="hero-eyebrow">AI-Powered Hiring Intelligence</div>
    <h1>Screen smarter,<br><strong>hire better.</strong></h1>
    <p class="hero-sub">Paste a job description and upload a resume — get an instant compatibility score, ranked strengths, skill gaps, and tailored interview questions in seconds.</p>
    <div class="hero-rule">
        <div class="hero-rule-line"></div>
        <div class="hero-rule-diamond"></div>
        <div class="hero-rule-line"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input Section ──────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="input-label">Job Description</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        label="jd", label_visibility="collapsed",
        placeholder="Paste the full job description here...\n\nExample:\nSenior Python Developer\n• 5+ years Python\n• FastAPI or Django\n• PostgreSQL & AWS",
        height=300,
    )

with col2:
    st.markdown('<div class="input-label">Candidate Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
    resume_text_input = st.text_area(
        label="Or paste resume text",
        placeholder="Paste resume text here if not uploading a file...",
        height=190,
    )

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    screen = st.button("⟶  Analyze Resume", use_container_width=True, type="primary")

# ── Helpers ────────────────────────────────────────────────────────────────────
def extract_text(f) -> str:
    name = f.name.lower()
    data = io.BytesIO(f.read())
    if name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(data)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith(".docx"):
        d = docx.Document(data)
        return "\n".join(p.text for p in d.paragraphs)
    elif name.endswith(".txt"):
        return data.read().decode("utf-8", errors="replace")
    return ""


def screen_resume(api_key, job_description, resume) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""You are a senior hiring expert. Evaluate this resume against the job description rigorously and honestly.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume}

Respond with valid JSON only — no markdown fences, no text outside the JSON:
{{
  "score": <integer 0-100>,
  "recommendation": "<exactly one of: strong yes | yes | maybe | no>",
  "top_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "gaps": ["<gap 1>", "<gap 2>"],
  "summary": "<2-3 sentence plain-English summary for a hiring manager>",
  "interview_questions": ["<question 1>", "<question 2>", "<question 3>"]
}}"""
    with st.spinner("Analyzing resume…"):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
    text = response.content[0].text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except json.JSONDecodeError:
                continue
    return json.loads(text)


def score_ring(score: int) -> str:
    if score >= 80:   color = "#5ebd8a"
    elif score >= 60: color = "#d4a853"
    else:             color = "#c97070"
    r = 60
    circumference = 2 * 3.14159 * r
    offset = circumference * (1 - score / 100)
    return f"""
    <div class="score-card">
        <div class="score-ring-wrap">
            <svg width="148" height="148" viewBox="0 0 148 148">
                <circle cx="74" cy="74" r="{r}" fill="none" stroke="#211d2e" stroke-width="8"/>
                <circle cx="74" cy="74" r="{r}" fill="none" stroke="{color}" stroke-width="8"
                    stroke-linecap="butt"
                    stroke-dasharray="{circumference:.1f}"
                    stroke-dashoffset="{offset:.1f}"/>
            </svg>
            <div class="score-center">
                <div class="score-num" style="color:{color}">{score}</div>
                <div class="score-denom">/ 100</div>
            </div>
        </div>
        <div class="score-bar-wrap">
            <div class="score-bar-label">
                <span>Match Score</span>
                <span style="color:{color};font-weight:600">{score}%</span>
            </div>
            <div class="score-bar-track">
                <div class="score-bar-fill" style="width:{score}%;background:{color}"></div>
            </div>
        </div>
    </div>"""


def verdict_card(recommendation: str, score: int) -> str:
    mapping = {
        "strong yes": ("#5ebd8a", "Strong Hire"),
        "yes":        ("#d4a853", "Proceed to Interview"),
        "maybe":      ("#c9a855", "Consider"),
        "no":         ("#c97070", "Pass"),
    }
    color, label = mapping.get(recommendation.lower(), ("#d4a853", recommendation.title()))
    if score >= 80:   level = "Excellent Match"
    elif score >= 60: level = "Good Match"
    else:             level = "Weak Match"
    return f"""
    <div class="verdict-card">
        <div>
            <div class="v-label">Hiring Decision</div>
            <div class="verdict-text" style="color:{color}">{label}</div>
        </div>
        <hr class="v-rule">
        <div>
            <div class="v-label">Match Level</div>
            <div class="match-text" style="color:{color}">{level}</div>
        </div>
    </div>"""


# ── Results ────────────────────────────────────────────────────────────────────
if screen:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    elif not job_description.strip():
        st.error("Please paste a job description.")
    else:
        resume = ""
        if uploaded_file:
            resume = extract_text(uploaded_file)
            if not resume.strip():
                st.error("Could not extract text from the file. Try pasting the resume instead.")
                st.stop()
        elif resume_text_input.strip():
            resume = resume_text_input.strip()
        else:
            st.error("Please upload a resume or paste resume text.")
            st.stop()

        try:
            result = screen_resume(api_key, job_description, resume)
            score = result["score"]

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="results-header">
                <div class="results-title">Analysis Report</div>
                <div class="results-sub">Match score: {score} / 100</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Row 1: score | verdict | summary ──────────────────────────────
            r1, r2, r3 = st.columns([1, 1, 2], gap="large")

            with r1:
                st.markdown(score_ring(score), unsafe_allow_html=True)

            with r2:
                st.markdown(verdict_card(result["recommendation"], score), unsafe_allow_html=True)

            with r3:
                st.markdown(f"""
                <div class="summary-card">
                    <div class="card-head">AI Summary</div>
                    <p>{result["summary"]}</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Row 2: strengths | gaps | questions ───────────────────────────
            b1, b2, b3 = st.columns(3, gap="large")

            with b1:
                st.markdown("""
                <div class="list-card">
                    <div class="card-head">Top Strengths</div>
                """, unsafe_allow_html=True)
                for s in result.get("top_strengths", []):
                    st.markdown(f'<div class="list-item li-green"><span class="li-icon">✓</span><span>{s}</span></div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with b2:
                st.markdown("""
                <div class="list-card">
                    <div class="card-head">Skill Gaps</div>
                """, unsafe_allow_html=True)
                gaps = result.get("gaps", [])
                if gaps:
                    for g in gaps:
                        st.markdown(f'<div class="list-item li-red"><span class="li-icon">✗</span><span>{g}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="list-item li-green"><span class="li-icon">✓</span><span>No significant gaps found</span></div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with b3:
                st.markdown("""
                <div class="list-card">
                    <div class="card-head">Interview Questions</div>
                """, unsafe_allow_html=True)
                for i, q in enumerate(result.get("interview_questions", []), 1):
                    st.markdown(f'<div class="list-item li-blue"><span class="li-icon">Q{i}</span><span>{q}</span></div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("Raw JSON"):
                st.json(result)

        except json.JSONDecodeError:
            st.error("Claude returned an unexpected format. Please try again.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
