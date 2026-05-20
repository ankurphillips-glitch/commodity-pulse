import streamlit as st
import anthropic
import json
import re
import pandas as pd
from datetime import datetime
from pathlib import Path

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CommodityPulse – Procurement Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants (no dates at module level) ──────────────────────────────────────
MAX_QUERIES = 2

DEFAULT_MATERIALS = sorted([
    "Aluminium Cans", "Aluminium Foil", "Aluminium Sheet", "Caustic Soda",
    "Cement", "Chlorine", "Cocoa Butter", "Copper Wire", "Corrugated Board",
    "Cotton Yarn", "Diesel Fuel", "Electricity (Industrial)", "Ethanol",
    "Flat Glass", "Flexible Packaging Film", "Float Glass", "Glass Bottles",
    "HDPE Resin", "Kraft Paper", "Labels & Sleeves", "LDPE Film",
    "Logistics - Air Freight", "Logistics - Road Freight", "Logistics - Sea Freight",
    "Natural Gas (Industrial)", "Newsprint", "Nitrogen Gas", "Palm Oil",
    "PET Bottles", "PET Resin", "Polypropylene Resin", "Shrink Wrap Film",
    "Silica Sand", "Soda Ash", "Soybean Oil", "Stainless Steel Coil",
    "Steel Coils (HRC)", "Sugar (Refined)", "Sulphuric Acid",
    "Timber (Softwood)", "Tissue Paper", "Wheat Flour", "White Sugar",
    "Wood Pulp", "Zinc (LME)",
])

RISK_CFG = {
    15: ("LOW",      "#22c55e", "#052e16", "#16a34a"),
    45: ("MODERATE", "#facc15", "#1c1a00", "#ca8a04"),
    70: ("HIGH",     "#f97316", "#1c0a00", "#ea580c"),
    98: ("CRITICAL", "#ef4444", "#1c0000", "#dc2626"),
}
VALID_SCORES = [15, 45, 70, 98]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; background:#080d16; color:#e5e7eb; }
.stApp { background:#080d16; }
.block-container { max-width:1100px; padding-top:1.5rem; padding-bottom:4rem; }
h1,h2,h3 { font-family:'DM Sans',sans-serif; color:#f9fafb; }
#MainMenu, footer, header { visibility:hidden; }

.topbar {
  display:flex; justify-content:space-between; align-items:center;
  padding:12px 20px; background:linear-gradient(90deg,#0f172a,#0a1628);
  border-bottom:1px solid #1e3a5f; border-radius:10px; margin-bottom:1.5rem;
}
.brand-name { font-weight:700; font-size:1rem; color:#f9fafb; }
.brand-sub  { font-size:0.62rem; color:#4b5563; letter-spacing:0.1em; }
.date-pill  {
  font-size:0.68rem; color:#4b5563; letter-spacing:0.08em;
  background:rgba(59,130,246,0.08); border:1px solid #1e3a5f;
  border-radius:6px; padding:4px 10px; font-family:'DM Mono',monospace;
}
.card {
  background:linear-gradient(135deg,#0f172a,#111827);
  border:1px solid #1e3a5f; border-radius:14px;
  padding:22px; margin-bottom:16px;
  box-shadow:0 4px 24px rgba(0,0,0,0.4);
}
.card-warn  { border-color:rgba(250,204,21,0.3) !important; }
.slabel {
  font-size:0.62rem; font-weight:700; color:#6b7280;
  letter-spacing:0.12em; text-transform:uppercase;
  margin-bottom:10px; font-family:'DM Mono',monospace;
}
.risk-badge {
  display:inline-block; border-radius:6px;
  padding:5px 14px; font-weight:700; font-size:0.78rem;
  letter-spacing:0.06em; font-family:'DM Mono',monospace;
}
.module-header {
  font-size:0.72rem; font-weight:700; color:#3b82f6;
  letter-spacing:0.15em; text-transform:uppercase;
  margin-bottom:4px; font-family:'DM Mono',monospace;
}
.module-title { font-size:1.15rem; font-weight:700; color:#f9fafb; margin-bottom:16px; }
.ft-table { width:100%; border-collapse:collapse; font-size:0.82rem; }
.ft-table th {
  background:#0f172a; color:#6b7280; font-size:0.62rem;
  letter-spacing:0.1em; text-transform:uppercase; padding:8px 12px;
  border-bottom:1px solid #1e3a5f; font-family:'DM Mono',monospace; text-align:left;
}
.ft-table td { padding:9px 12px; border-bottom:1px solid #0f172a; color:#d1d5db; vertical-align:top; }
.ft-table tr:last-child td { border-bottom:none; }
.ft-key { color:#93c5fd; font-family:'DM Mono',monospace; font-size:0.78rem; white-space:nowrap; }
.ch-table { width:100%; border-collapse:collapse; font-size:0.8rem; margin-top:8px; }
.ch-table th {
  background:#0a1121; color:#6b7280; font-size:0.6rem;
  letter-spacing:0.1em; text-transform:uppercase; padding:9px 12px;
  border-bottom:2px solid #1e3a5f; font-family:'DM Mono',monospace; text-align:left;
}
.ch-table td { padding:9px 12px; border-bottom:1px solid #0f172a; color:#d1d5db; vertical-align:top; line-height:1.55; }
.ch-table tr:last-child td { border-bottom:none; }
.weight-pill {
  display:inline-block; background:rgba(59,130,246,0.15);
  border:1px solid rgba(59,130,246,0.4); border-radius:20px;
  padding:2px 9px; font-weight:700; color:#93c5fd;
  font-family:'DM Mono',monospace; font-size:0.78rem;
}
.proxy-tag {
  display:inline-block; background:rgba(250,204,21,0.1);
  border:1px solid rgba(250,204,21,0.3); border-radius:4px;
  padding:1px 6px; font-size:0.68rem; color:#fde68a;
  font-family:'DM Mono',monospace; margin-left:4px;
}
.inf-table { width:100%; border-collapse:collapse; font-size:0.8rem; }
.inf-table th {
  background:#0a1121; color:#6b7280; font-size:0.6rem;
  letter-spacing:0.1em; text-transform:uppercase; padding:8px 12px;
  border-bottom:2px solid #1e3a5f; font-family:'DM Mono',monospace; text-align:left;
}
.inf-table td { padding:9px 12px; border-bottom:1px solid #0f172a; color:#d1d5db; vertical-align:top; }
.inf-table tr:last-child td { border-bottom:none; }
.inf-pos { color:#f97316; font-weight:700; font-family:'DM Mono',monospace; }
.inf-neg { color:#22c55e; font-weight:700; font-family:'DM Mono',monospace; }
.inf-neu { color:#facc15; font-weight:700; font-family:'DM Mono',monospace; }
.inf-total { background:rgba(59,130,246,0.08) !important; font-weight:700; }
.bullet-block {
  border-left:2px solid #1e3a5f; padding:10px 14px;
  margin-bottom:10px; border-radius:0 6px 6px 0;
  background:rgba(255,255,255,0.02);
}
.bullet-title { color:#93c5fd; font-weight:600; font-size:0.84rem; }
.bullet-body  { color:#d1d5db; font-size:0.82rem; line-height:1.65; margin-top:4px; }
.scenario-best  { border-left:3px solid #22c55e; padding:10px 14px; background:rgba(34,197,94,0.04);  border-radius:0 8px 8px 0; margin-bottom:8px; }
.scenario-base  { border-left:3px solid #facc15; padding:10px 14px; background:rgba(250,204,21,0.04); border-radius:0 8px 8px 0; margin-bottom:8px; }
.scenario-worst { border-left:3px solid #ef4444; padding:10px 14px; background:rgba(239,68,68,0.04);  border-radius:0 8px 8px 0; margin-bottom:8px; }
.sc-label { font-size:0.62rem; font-weight:700; letter-spacing:0.1em; margin-bottom:4px; font-family:'DM Mono',monospace; }
.sc-text  { font-size:0.82rem; color:#d1d5db; line-height:1.6; }
.scope-note {
  background:rgba(59,130,246,0.06); border:1px solid rgba(59,130,246,0.2);
  border-radius:8px; padding:12px 16px;
  font-size:0.8rem; color:#93c5fd; line-height:1.6; margin-bottom:16px;
}
.conf-high { color:#22c55e; font-weight:700; }
.conf-med  { color:#facc15; font-weight:700; }
.conf-low  { color:#f97316; font-weight:700; }
.ref-link { font-size:0.7rem; color:#3b82f6; word-break:break-all; line-height:1.9; font-family:'DM Mono',monospace; }
div[data-testid="stButton"] button {
  background:linear-gradient(135deg,#1d4ed8,#2563eb);
  color:#fff; font-weight:700; border:none; border-radius:10px;
  padding:0.55rem 2rem; font-family:'DM Sans',sans-serif;
  font-size:0.9rem; letter-spacing:0.04em;
}
div[data-testid="stButton"] button:hover {
  background:linear-gradient(135deg,#2563eb,#3b82f6);
  box-shadow:0 0 20px rgba(59,130,246,0.3);
}
</style>
""", unsafe_allow_html=True)


# ── Utility functions ─────────────────────────────────────────────────────────

def today_str():
    """Always returns the actual current date. Never cached."""
    return datetime.today().strftime("%d %B %Y")


def get_api_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        st.error("API key not configured. Go to Streamlit Cloud > Settings > Secrets and add: ANTHROPIC_API_KEY = \"sk-ant-...\"")
        st.stop()


def load_materials():
    try:
        df = pd.read_excel("materials.xlsx")
        for col in ["Material", "material", "L3 Category", "Category", "Service", "Name"]:
            if col in df.columns:
                items = df[col].dropna().astype(str).str.strip().tolist()
                items = [i for i in items if i]
                if items:
                    return sorted(items)
        col0 = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
        return sorted([i for i in col0 if i]) or DEFAULT_MATERIALS
    except Exception:
        return DEFAULT_MATERIALS


def snap_risk(score):
    try:
        score = int(float(score))
    except Exception:
        return 45
    return min(VALID_SCORES, key=lambda x: abs(x - score))


def risk_badge_html(score):
    score = snap_risk(score)
    label, color, bg, border = RISK_CFG[score]
    return (f'<span class="risk-badge" style="color:{color};background:{bg};border:1.5px solid {border};">'
            f'● {score} — {label}</span>')


def conf_class(level):
    l = str(level).lower()
    if "high" in l:
        return "conf-high"
    if "low" in l:
        return "conf-low"
    return "conf-med"


def month_labels(n):
    from datetime import date
    import calendar
    d = date.today()
    labels = []
    for _ in range(n):
        month = d.month % 12 + 1
        year  = d.year + (1 if d.month == 12 else 0)
        d = d.replace(year=year, month=month, day=1)
        labels.append(d.strftime("%B %Y"))
    return labels


def extract_all_text(response):
    """Extract all text blocks from an Anthropic response object."""
    parts = []
    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            parts.append(block.text.strip())
    return "\n\n".join(parts)


def safe_parse_json(text):
    """Parse JSON from model output with multiple fallback strategies."""
    text = text.strip()
    # Strip markdown fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    # Find the JSON object
    m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        raise ValueError("No JSON object found in response.")
    raw = m.group()
    # Try direct parse first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Remove control characters except tab/newline/CR
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Replace smart quotes
    cleaned = cleaned.replace('\u2018', "'").replace('\u2019', "'")
    cleaned = cleaned.replace('\u201c', '"').replace('\u201d', '"')
    cleaned = cleaned.replace('\u2013', '-').replace('\u2014', '-')
    cleaned = cleaned.replace('\u00a0', ' ')
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse failed after all cleanup attempts: {e}")


# ── Two-step API architecture ─────────────────────────────────────────────────
# Step 1: gather research using web search (free-form text output)
# Step 2: structure the research into clean JSON (no web search, no special chars)

def _research(client, research_prompt):
    """Step 1 — web search enabled, returns plain text research."""
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": research_prompt}],
    )
    return extract_all_text(response)


def _structure(client, research_text, schema_prompt):
    """Step 2 — no web search, returns clean JSON every time."""
    prompt = (
        f"You have the following research notes:\n\n{research_text}\n\n"
        f"{schema_prompt}\n\n"
        "CRITICAL RULES FOR YOUR RESPONSE:\n"
        "- Return ONLY the raw JSON object. No markdown. No explanation. No preamble.\n"
        "- Use ONLY standard ASCII characters inside all string values.\n"
        "- Replace ALL em-dashes and en-dashes with a plain hyphen: -\n"
        "- Replace ALL smart/curly quotes with standard straight quotes.\n"
        "- Do NOT use any Unicode characters, symbols, or special punctuation.\n"
        "- Every string value must be plain readable English with no special formatting.\n"
        "- The output must be valid JSON parseable by Python's json.loads()."
    )
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return safe_parse_json(extract_all_text(response))


# ── Module 1: Cost Head Analysis ──────────────────────────────────────────────

def run_module1(material, region, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    today = today_str()

    research_prompt = (
        f"You are a senior procurement cost analyst. Today is {today}.\n"
        f"Research the cost structure for: {material} in {region}.\n"
        f"Find the most current benchmark indices, price series, and proxies available for this material.\n"
        f"Identify 4-6 cost heads (e.g. Energy, Raw Materials, Labour, Logistics, etc.) with their approximate weight percentages summing to 100%.\n"
        f"For each cost head, identify the best public benchmark index or proxy available in {region}.\n"
        f"Note the confidence level (High / Medium / Low) based on data availability.\n"
        f"Also note the tax basis (e.g. Ex-works, DAP, Duty Paid) most relevant for {region}.\n"
        f"Provide specific index names, issuing bodies, and most recent data dates where available."
    )

    research_text = _research(client, research_prompt)

    schema_prompt = (
        f"Structure the research into this exact JSON schema:\n"
        f'{{\n'
        f'  "scope_note": "One sentence describing whether direct pricing is available or proxies are used.",\n'
        f'  "freshness": {{\n'
        f'    "check_date": "{today}",\n'
        f'    "region": "{region}",\n'
        f'    "tax_basis": "e.g. Duty Paid Rotterdam",\n'
        f'    "primary_benchmarks": "Comma-separated list of main indices used",\n'
        f'    "most_recent_source_date": "DD Mon YYYY",\n'
        f'    "confidence_level": "High or Medium or Low",\n'
        f'    "narrative": "2-3 sentences on data quality and where proxies are used."\n'
        f'  }},\n'
        f'  "cost_heads": [\n'
        f'    {{\n'
        f'      "name": "Cost head name",\n'
        f'      "weight_pct": 30,\n'
        f'      "why_included": "One sentence on why this cost head matters.",\n'
        f'      "best_fit_index": "Name of index or proxy",\n'
        f'      "why_index": "One sentence on why this is the best public fit.",\n'
        f'      "is_proxy": false\n'
        f'    }}\n'
        f'  ]\n'
        f'}}\n'
        f'Weights must sum to exactly 100. is_proxy is true when no direct price series exists.'
    )

    return _structure(client, research_text, schema_prompt)


# ── Module 2: Inflation Impact ────────────────────────────────────────────────

def run_module2(material, region, periods, cost_heads, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    today = today_str()
    labels = month_labels(periods)
    ch_list = ", ".join([f"{c['name']} ({c['weight_pct']}%)" for c in cost_heads])

    research_prompt = (
        f"You are a senior procurement cost analyst. Today is {today}.\n"
        f"Research forward price signals for: {material} in {region}.\n"
        f"Cost heads to cover: {ch_list}\n"
        f"Find the latest futures curves, analyst forecasts, and forward price signals for each cost head benchmark.\n"
        f"Months to project: {labels}\n"
        f"For each month and each cost head, estimate the percentage change in input cost vs current levels.\n"
        f"Provide specific data: futures levels, consensus ranges, or clearly labelled estimates.\n"
        f"Focus entirely on {region} context."
    )

    research_text = _research(client, research_prompt)

    months_schema = []
    for label in labels:
        impacts = [{"name": c["name"], "weight_pct": c["weight_pct"],
                    "projected_change_pct": 0.0, "direction": "stable",
                    "driver": "driver sentence"} for c in cost_heads]
        months_schema.append({
            "label": label,
            "cost_head_impacts": impacts,
            "weighted_total_pct": 0.0,
            "key_driver": "dominant factor sentence"
        })

    schema_prompt = (
        f"Structure the research into this exact JSON schema for {periods} months.\n"
        f"projected_change_pct = estimated % change in that cost head vs current levels. Positive = cost increase.\n"
        f"weighted_total_pct = sum of (projected_change_pct * weight_pct / 100) across all cost heads for that month.\n"
        f'{{\n'
        f'  "analysis_basis": "One sentence on data sources used.",\n'
        f'  "months": [\n'
        f'    {{\n'
        f'      "label": "Month Year",\n'
        f'      "cost_head_impacts": [\n'
        f'        {{\n'
        f'          "name": "Cost head name",\n'
        f'          "weight_pct": 30,\n'
        f'          "projected_change_pct": 2.5,\n'
        f'          "direction": "up or down or stable",\n'
        f'          "driver": "Short plain driver sentence."\n'
        f'        }}\n'
        f'      ],\n'
        f'      "weighted_total_pct": 1.1,\n'
        f'      "key_driver": "One sentence on dominant factor."\n'
        f'    }}\n'
        f'  ],\n'
        f'  "key_assumptions": "2 sentences on main assumptions.",\n'
        f'  "disclaimer": "Estimate based on public forward signals as of {today}. Not a financial model."\n'
        f'}}\n'
        f'Months to include: {labels}. All values must be numbers, not strings.'
    )

    return _structure(client, research_text, schema_prompt)


# ── Module 3: Shortage Tracker ────────────────────────────────────────────────

def run_module3(material, region, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    today = today_str()

    research_prompt = (
        f"You are a senior procurement supply risk analyst. Today is {today}.\n"
        f"Research the supply risk situation for: {material} in {region}.\n"
        f"Search for the most current data on:\n"
        f"- Production issues, plant shutdowns, capacity changes\n"
        f"- Trade flows, import dependence, export restrictions\n"
        f"- Logistics constraints, freight rates, port disruptions\n"
        f"- Geopolitical exposure, sanctions, policy changes\n"
        f"- Energy input risks, carbon costs\n"
        f"- Weather impacts on production or logistics\n"
        f"- Downstream L3 category impacts\n"
        f"Provide specific figures, dates, and source names. Focus entirely on {region}.\n"
        f"Also provide: a 6-month availability outlook, and best/base/worst case 12-month scenarios.\n"
        f"Include 3-4 buyer watchpoints or concentration risk observations.\n"
        f"List the URLs of all sources consulted."
    )

    research_text = _research(client, research_prompt)

    schema_prompt = (
        f"Structure the research into this exact JSON schema.\n"
        f"current_supply_risk and forecasted_supply_risk must be ONLY one of: 15, 45, 70, or 98.\n"
        f"15 = least risk. 98 = highest risk.\n"
        f'{{\n'
        f'  "current_supply_risk": 45,\n'
        f'  "forecasted_supply_risk": 70,\n'
        f'  "variables": [\n'
        f'    {{\n'
        f'      "title": "Short descriptive title",\n'
        f'      "body": "3-5 factual sentences with specific figures and dates."\n'
        f'    }}\n'
        f'  ],\n'
        f'  "forecast_6m": "3-4 sentences on 6-month availability outlook from {today}.",\n'
        f'  "forecast_12m_best": "One sentence best-case scenario.",\n'
        f'  "forecast_12m_base": "One sentence base-case scenario.",\n'
        f'  "forecast_12m_worst": "One sentence worst-case scenario.",\n'
        f'  "additional_comments": [\n'
        f'    {{\n'
        f'      "title": "Short watchpoint title",\n'
        f'      "body": "2-4 sentences on downstream impacts or buyer watchpoints.",\n'
        f'      "references": ["https://example.com/source"]\n'
        f'    }}\n'
        f'  ],\n'
        f'  "all_references": ["https://example.com/ref1"]\n'
        f'}}\n'
        f'Provide 4-6 variable bullets and 3-4 additional comment bullets with real source URLs.'
    )

    return _structure(client, research_text, schema_prompt)


# ── Display: Module 1 ─────────────────────────────────────────────────────────

def display_module1(d, material, region):
    f  = d.get("freshness", {})
    ch = d.get("cost_heads", [])

    st.markdown('<div class="module-header">MODULE 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Cost Head Analysis</div>', unsafe_allow_html=True)

    scope = d.get("scope_note", "")
    if scope:
        st.markdown(f'<div class="scope-note">{material} ({region}) — {scope}</div>',
                    unsafe_allow_html=True)

    # Freshness block
    st.markdown('<div class="slabel">B. Freshness Block</div>', unsafe_allow_html=True)
    conf = f.get("confidence_level", "Medium")
    rows_html = "".join([
        f'<tr><td class="ft-key">Market status check date</td><td>{f.get("check_date", today_str())}</td></tr>',
        f'<tr><td class="ft-key">Region</td><td>{f.get("region", region)}</td></tr>',
        f'<tr><td class="ft-key">Tax basis</td><td>{f.get("tax_basis", "N/A")}</td></tr>',
        f'<tr><td class="ft-key">Primary benchmark(s) used</td><td>{f.get("primary_benchmarks", "-")}</td></tr>',
        f'<tr><td class="ft-key">Most recent source date found</td><td>{f.get("most_recent_source_date", "-")}</td></tr>',
        f'<tr><td class="ft-key">Confidence level</td>'
        f'<td><span class="{conf_class(conf)}">{conf}</span></td></tr>',
    ])
    st.markdown(
        f'<div class="card"><table class="ft-table"><thead><tr><th>Item</th><th>Value</th>'
        f'</tr></thead><tbody>{rows_html}</tbody></table></div>',
        unsafe_allow_html=True,
    )
    narrative = f.get("narrative", "")
    if narrative:
        st.markdown(
            f'<div class="card" style="padding:14px 20px;">'
            f'<div style="font-size:0.82rem;color:#d1d5db;line-height:1.7;">{narrative}</div></div>',
            unsafe_allow_html=True,
        )

    # Cost-head table
    st.markdown('<div class="slabel" style="margin-top:16px;">C. Cost-Head Table</div>',
                unsafe_allow_html=True)
    ch_rows = ""
    for c in ch:
        proxy_tag = '<span class="proxy-tag">PROXY</span>' if c.get("is_proxy") else ""
        ch_rows += (
            f'<tr>'
            f'<td><strong style="color:#f9fafb;">{c.get("name","")}</strong></td>'
            f'<td><span class="weight-pill">{c.get("weight_pct",0)}%</span></td>'
            f'<td>{c.get("why_included","")}</td>'
            f'<td>{c.get("best_fit_index","")}{proxy_tag}</td>'
            f'<td>{c.get("why_index","")}</td>'
            f'</tr>'
        )
    st.markdown(
        f'<div class="card"><table class="ch-table"><thead><tr>'
        f'<th>Cost Head</th><th>Weight %</th><th>Why Included</th>'
        f'<th>Best-Fit Index / Proxy</th><th>Why This Index</th>'
        f'</tr></thead><tbody>{ch_rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )
    return ch


# ── Display: Module 2 ─────────────────────────────────────────────────────────

def display_module2(d):
    st.markdown('<hr style="border:none;border-top:1px solid #1e3a5f;margin:20px 0;">',
                unsafe_allow_html=True)
    st.markdown('<div class="module-header">MODULE 2</div>', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Inflation Impact Projection</div>', unsafe_allow_html=True)

    basis = d.get("analysis_basis", "")
    if basis:
        st.markdown(f'<div class="scope-note">{basis}</div>', unsafe_allow_html=True)

    months = d.get("months", [])
    if months:
        heads = [h.get("name", "") for h in months[0].get("cost_head_impacts", [])]
        th = "".join(f"<th>{h}</th>" for h in heads)
        header = f"<tr><th>Month</th>{th}<th>Weighted Total</th><th>Key Driver</th></tr>"

        rows_html = ""
        for m in months:
            cells = ""
            for imp in m.get("cost_head_impacts", []):
                try:
                    pct = float(imp.get("projected_change_pct", 0))
                except (TypeError, ValueError):
                    pct = 0.0
                css = "inf-pos" if pct > 0 else ("inf-neg" if pct < 0 else "inf-neu")
                sign = "+" if pct > 0 else ""
                driver = imp.get("driver", "")
                cells += (f'<td class="{css}">{sign}{pct:.1f}%'
                          f'<br><span style="font-size:0.68rem;color:#6b7280;font-weight:400;">'
                          f'{driver}</span></td>')
            try:
                total = float(m.get("weighted_total_pct", 0))
            except (TypeError, ValueError):
                total = 0.0
            t_css  = "inf-pos" if total > 0 else ("inf-neg" if total < 0 else "inf-neu")
            sign   = "+" if total > 0 else ""
            rows_html += (
                f'<tr>'
                f'<td style="color:#f9fafb;font-weight:600;white-space:nowrap;">{m.get("label","")}</td>'
                f'{cells}'
                f'<td class="inf-total {t_css}">{sign}{total:.2f}%</td>'
                f'<td style="font-size:0.78rem;color:#d1d5db;">{m.get("key_driver","")}</td>'
                f'</tr>'
            )
        st.markdown(
            f'<div class="card" style="overflow-x:auto;">'
            f'<table class="inf-table"><thead>{header}</thead><tbody>{rows_html}</tbody></table></div>',
            unsafe_allow_html=True,
        )

    assumptions = d.get("key_assumptions", "")
    if assumptions:
        st.markdown(
            f'<div class="card card-warn"><div class="slabel">Key Assumptions</div>'
            f'<div style="font-size:0.82rem;color:#d1d5db;line-height:1.7;">{assumptions}</div></div>',
            unsafe_allow_html=True,
        )
    disclaimer = d.get("disclaimer", "")
    if disclaimer:
        st.markdown(
            f'<div style="font-size:0.72rem;color:#4b5563;margin-top:6px;">&#9888; {disclaimer}</div>',
            unsafe_allow_html=True,
        )


# ── Display: Module 3 ─────────────────────────────────────────────────────────

def display_module3(d):
    st.markdown('<hr style="border:none;border-top:1px solid #1e3a5f;margin:20px 0;">',
                unsafe_allow_html=True)
    st.markdown('<div class="module-header">MODULE 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Shortage Tracker</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="card"><div class="slabel">Current Supply Risk</div>'
            f'{risk_badge_html(d.get("current_supply_risk", 45))}</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="card"><div class="slabel">Forecasted Supply Risk</div>'
            f'{risk_badge_html(d.get("forecasted_supply_risk", 45))}</div>',
            unsafe_allow_html=True,
        )

    variables = d.get("variables", [])
    if variables:
        st.markdown('<div class="slabel" style="margin-top:8px;">Variables Impacting Availability</div>',
                    unsafe_allow_html=True)
        html = '<div class="card">'
        for v in variables:
            html += (f'<div class="bullet-block">'
                     f'<div class="bullet-title">&gt; {v.get("title","")}</div>'
                     f'<div class="bullet-body">{v.get("body","")}</div>'
                     f'</div>')
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    st.markdown('<div class="slabel" style="margin-top:4px;">Availability Forecast</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="card">'
        f'<div class="slabel" style="color:#4b5563;">6-Month Outlook</div>'
        f'<div style="font-size:0.82rem;color:#d1d5db;line-height:1.7;margin-bottom:16px;">'
        f'&gt; Next 6 months: {d.get("forecast_6m","")}</div>'
        f'<div class="slabel" style="color:#4b5563;">12-Month Scenarios</div>'
        f'<div class="scenario-best"><div class="sc-label" style="color:#22c55e;">&#9650; BEST CASE</div>'
        f'<div class="sc-text">{d.get("forecast_12m_best","")}</div></div>'
        f'<div class="scenario-base"><div class="sc-label" style="color:#facc15;">&#9670; BASE CASE</div>'
        f'<div class="sc-text">{d.get("forecast_12m_base","")}</div></div>'
        f'<div class="scenario-worst"><div class="sc-label" style="color:#ef4444;">&#9660; WORST CASE</div>'
        f'<div class="sc-text">{d.get("forecast_12m_worst","")}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    comments = d.get("additional_comments", [])
    if comments:
        st.markdown('<div class="slabel" style="margin-top:4px;">Additional Comments</div>',
                    unsafe_allow_html=True)
        html = '<div class="card">'
        for c in comments:
            refs_html = "".join(
                f'<a href="{r}" target="_blank" class="ref-link">{r}</a><br>'
                for r in c.get("references", [])
            )
            html += (f'<div class="bullet-block">'
                     f'<div class="bullet-title">&gt; {c.get("title","")}</div>'
                     f'<div class="bullet-body">{c.get("body","")}</div>'
                     f'{"<div style=margin-top:6px;>" + refs_html + "</div>" if refs_html else ""}'
                     f'</div>')
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    all_refs = d.get("all_references", [])
    if all_refs:
        with st.expander("All References"):
            for r in all_refs:
                st.markdown(
                    f'<a href="{r}" target="_blank" class="ref-link">{r}</a>',
                    unsafe_allow_html=True,
                )


# ── Session state ─────────────────────────────────────────────────────────────
for key in ["query_count", "result_m1", "result_m2", "result_m3", "last_params"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key == "query_count" else None

materials_list = load_materials()

# ── Top bar (date computed fresh on every render) ─────────────────────────────
current_date = datetime.today().strftime("%d %b %Y").upper()
st.markdown(
    f'<div class="topbar">'
    f'<div><div class="brand-name">&#11203; CommodityPulse</div>'
    f'<div class="brand-sub">PROCUREMENT INTELLIGENCE PLATFORM</div></div>'
    f'<div class="date-pill">ANALYSIS DATE: {current_date}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Analysis Parameters")
    st.markdown("---")

    selected_material = st.selectbox(
        "Select L3 Category / Material",
        options=materials_list,
        help="Select the material or service to analyse.",
    )
    selected_region = st.selectbox(
        "Region",
        options=["Europe", "North America", "Asia Pacific", "Middle East & Africa", "Latin America"],
        index=0,
    )

    st.markdown("---")
    st.markdown("**Select Analysis Modules**")
    run_m2 = st.checkbox("Module 2 — Inflation Impact", value=False)
    run_m3 = st.checkbox("Module 3 — Shortage Tracker", value=False)

    forecast_periods = 3
    if run_m2:
        forecast_periods = st.select_slider(
            "Forecast period (months)",
            options=[1, 2, 3, 4, 5, 6],
            value=3,
        )

    st.markdown("---")
    queries_left = MAX_QUERIES - st.session_state["query_count"]
    if queries_left > 0:
        st.markdown(
            f'<div style="font-size:0.72rem;color:#6b7280;font-family:\'DM Mono\',monospace;">'
            f'Trial queries remaining: <strong style="color:#f9fafb;">{queries_left} / {MAX_QUERIES}</strong></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="font-size:0.72rem;color:#ef4444;font-family:\'DM Mono\',monospace;">'
            'Trial limit reached. Contact us to unlock full access.</div>',
            unsafe_allow_html=True,
        )

    analyse_btn = st.button("Run Analysis →", use_container_width=True, disabled=(queries_left <= 0))

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.68rem;color:#374151;line-height:1.9;">'
        'Module 1 always runs.<br>'
        'Module 2 requires Module 1 output.<br>'
        'Module 3 fetches live supply data.<br><br>'
        '&#9888; All outputs are AI-generated estimates.<br>Validate before decisions.'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Run analysis ──────────────────────────────────────────────────────────────
if analyse_btn:
    api_key = get_api_key()
    st.session_state["query_count"] += 1
    st.session_state["result_m1"] = None
    st.session_state["result_m2"] = None
    st.session_state["result_m3"] = None
    st.session_state["last_params"] = {
        "material": selected_material,
        "region": selected_region,
        "run_m2": run_m2,
        "run_m3": run_m3,
        "periods": forecast_periods,
    }

    with st.spinner(f"Module 1 — Researching cost structure for {selected_material}..."):
        try:
            st.session_state["result_m1"] = run_module1(selected_material, selected_region, api_key)
        except Exception as e:
            st.error(f"Module 1 error: {e}")

    if run_m2 and st.session_state["result_m1"]:
        cost_heads = st.session_state["result_m1"].get("cost_heads", [])
        with st.spinner(f"Module 2 — Projecting inflation impact over {forecast_periods} months..."):
            try:
                st.session_state["result_m2"] = run_module2(
                    selected_material, selected_region, forecast_periods, cost_heads, api_key
                )
            except Exception as e:
                st.error(f"Module 2 error: {e}")

    if run_m3:
        with st.spinner(f"Module 3 — Fetching live supply risk data..."):
            try:
                st.session_state["result_m3"] = run_module3(selected_material, selected_region, api_key)
            except Exception as e:
                st.error(f"Module 3 error: {e}")

# ── Display results ───────────────────────────────────────────────────────────
p   = st.session_state.get("last_params") or {}
mat = p.get("material", "")
reg = p.get("region", "Europe")

if st.session_state["result_m1"]:
    st.markdown(
        f'<div style="font-size:0.68rem;color:#6b7280;margin-bottom:4px;font-family:\'DM Mono\',monospace;">RESULTS FOR</div>'
        f'<h2 style="margin:0 0 20px 0;">{mat} <span style="color:#3b82f6;">({reg})</span></h2>',
        unsafe_allow_html=True,
    )
    cost_heads = display_module1(st.session_state["result_m1"], mat, reg)

    if st.session_state["result_m2"]:
        display_module2(st.session_state["result_m2"])

    if st.session_state["result_m3"]:
        display_module3(st.session_state["result_m3"])

    with st.expander("Copy-paste output for Excel"):
        m1 = st.session_state["result_m1"]
        m3 = st.session_state["result_m3"]
        ch_str = " | ".join(f'{c["name"]} {c["weight_pct"]}%' for c in m1.get("cost_heads", []))
        row = "\t".join([
            mat, reg,
            str(m3.get("current_supply_risk", "")) if m3 else "",
            str(m3.get("forecasted_supply_risk", "")) if m3 else "",
            ch_str,
            m1.get("freshness", {}).get("confidence_level", ""),
            today_str(), "TBC"
        ])
        st.code(row, language=None)

elif not analyse_btn:
    st.markdown(
        '<div style="text-align:center;padding:80px 24px;color:#374151;">'
        '<div style="font-size:2rem;margin-bottom:12px;">&#11203;</div>'
        '<div style="font-size:1rem;color:#4b5563;">Select a material and region in the sidebar,<br>'
        'choose your modules, and click <strong style="color:#93c5fd;">Run Analysis</strong>.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;margin-top:3rem;padding-top:1.5rem;'
    'border-top:1px solid #0f172a;font-size:0.68rem;color:#374151;line-height:2;">'
    'CommodityPulse &nbsp;·&nbsp; Procurement Intelligence Platform<br>'
    'Powered by Anthropic Claude with live web search &nbsp;·&nbsp; Built for procurement teams'
    '</div>',
    unsafe_allow_html=True,
)
