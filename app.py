import streamlit as st
import anthropic
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CommodityPulse – Procurement Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 349 L3 Categories ─────────────────────────────────────────────────────────
CATEGORIES = [
    "CARPENTER (BUILDING MATERIALS)","CEILING (BUILDING MATERIALS)","COOLING (BUILDING MATERIALS)",
    "DOORS (BUILDING MATERIALS)","ELECTRICITY HV (BUILDING MATERIALS)","ELECTRICITY LV (BUILDING MATERIALS)",
    "ELEVATORS (BUILDING MATERIALS)","EMERGENCY GENERATORS & UPS (NO-BREAK) (BUILDING MATERIALS)",
    "FLOOR LAYER (BUILDING MATERIALS)","HVAC (BUILDING MATERIALS)","LIGHTING INDOOR (BUILDING MATERIALS)",
    "LIGHTING OUTDOOR (BUILDING MATERIALS)","OTHER (BUILDING MATERIALS)","PAINTER (BUILDING MATERIALS)",
    "PLUMBER/SEWER (BUILDING MATERIALS)","ADVISORY SERVICES","ARCHITECT","CARCASE WORKS",
    "CARPENTER (CONTRACTORS)","CEILING (CONTRACTORS)","COOLING (CONTRACTORS)","COORDINATION",
    "DATA CABLES","DEMOLITION","DOORS (CONTRACTORS)","ELECTRICITY HV (CONTRACTORS)",
    "ELECTRICITY LV (CONTRACTORS)","ELEVATORS (CONTRACTORS)",
    "EMERGENCY GENERATORS & UPS (NO-BREAK) (CONTRACTORS)","ENGINEERING",
    "FIRE SAFETY (CONTRACTORS)","FLOOR LAYER (CONTRACTORS)","GENERAL CONTRACTORS",
    "HVAC (CONTRACTORS)","INFRASTRUCTURE OUTSOURCING SERVICES (CONTRACTORS)","OTHER (CONTRACTORS)",
    "PAINTER (CONTRACTORS)","PLUMBER/SEWER (CONTRACTORS)","ROOF WORK","SECURITY SYSTEM",
    "SHELVING (CONTRACTORS)","SIGNING (CONTRACTORS)",
    "BUILDINGS / COLD SHELL (EXTERIOR REAL ESTATE)","BUILDINGS / HOT SHELL (INTERIOR FORMAT BASED)",
    "COOLING (MAINTENANCE)","ELECTRICITY HV (MAINTENANCE)","ELECTRICITY LV (MAINTENANCE)",
    "ELEVATORS (MAINTENANCE)","EMERGENCY GENERATORS & UPS (NO-BREAK) (MAINTENANCE)",
    "FIRE SAFETY (MAINTENANCE)","GROUNDS / SURROUNDINGS (F.E. PARKING FACILITIES)",
    "HVAC (MAINTENANCE)","LIGHTING INDOOR (MAINTENANCE)","LIGHTING OUTDOOR (MAINTENANCE)",
    "OTHER (MAINTENANCE)","PLUMBER/SEWER (MAINTENANCE)","WATER TREATMENT / SANITARY",
    "SITE LEASE FOR STORES & PARKING","SITE PURCHASES AND SALES FOR STORES & PARKING",
    "CREATIVE/DIGITAL CONSULTANCY","IT CONSULTANCY","LEGAL CONSULTANCY","MANAGEMENT CONSULTANCY",
    "MEMBERSHIPS & SPONSORING (NON MARKETING)","QUALITY TESTING/CERTIFICATION",
    "STRATEGY CONSULTANCY","SUPPLY CHAIN CONSULTANCY","TAX CONSULTANCY",
    "OTHER (EXTERNAL HIRING)","TEMP LABOR FOR STORES","TEMP LABOR FOR WAREHOUSES",
    "FINANCE & ACCOUNTING SERVICES","FINANCIAL AUDIT SERVICES","GENERAL BANKING SERVICES",
    "INSURANCES","LEASING (EMPLOYEE CARS/VANS)","MONEY HANDLING AND TRANSPORT",
    "PAYMENT TRANSACTION FEES","ADMINISTRATIVE PAYROLL","EMPLOYEE BENEFITS","HEALTH SERVICES",
    "LEARNING & DEVELOPMENT","OTHER MOBILITY SOLUTIONS","OUTPLACEMENT","RECRUITMENT SERVICES",
    "AIRLINE TICKETS","BOOKING AGENCIES AND TOOLS","EVENTS (TRAVEL & EVENTS)",
    "EXTERNAL LOCATIONS","HOTEL (NIGHTS)","OTHER TRANSPORT (NON COMMUTING)",
    "CABINETS PLUG-IN (COOLING)","CABINETS REMOTE (COOLING)","OTHER (COOLING)",
    "FURNITURE MIXED MATERIALS","FURNITURE/FIXTURES BACK OFFICE, HQ, CANTEEN (FURNITURE)",
    "FURNITURE/FIXTURES STORE CASH WRAPS/CHECKOUTS (FURNITURE)",
    "FURNITURE/FIXTURES STORE INOX/STEEL (FURNITURE)","FURNITURE/FIXTURES STORE PLASTIC",
    "FURNITURE/FIXTURES STORE WOOD (FURNITURE)","OTHER (FURNITURE)","SHELVING (FURNITURE)",
    "(SHELL)FISH PROCESSING MACHINES (MACHINERY)","AUDIO/SOUND EQUIPMENT (MACHINERY)",
    "BREAD PROCESSING MACHINES (MACHINERY)","CHEESE PROCESSING MACHINES (MACHINERY)",
    "CLEANING MACHINES/CLEANING DISPENSER (MACHINERY)","COFFEE MACHINES (MACHINERY)",
    "DELI EQUIPMENT & UTENSILS (MACHINERY)","FRUIT & VEG PROCESSING MACHINES (MACHINERY)",
    "GRILLS (MACHINERY)","MEAT PROCESSING MACHINES (MACHINERY)","OTHER (MACHINERY)",
    "OVENS (MACHINERY)","PACKING MACHINE (MACHINERY)","PAPER PROCESSING MACHINES (MACHINERY)",
    "REVERSE VENDING MACHINES (MACHINERY)","VENDING MACHINES (MACHINERY)",
    "WEIGHING EQUIPMENT (MACHINERY)","CABINETS PLUG-IN (MAINTENANCE COOLING)",
    "CABINETS REMOTE (MAINTENANCE COOLING)","OTHER (MAINTENANCE COOLING)",
    "FURNITURE/FIXTURES BACK OFFICE, HQ, CANTEEN (MAINTENANCE FURNITURE)",
    "FURNITURE/FIXTURES STORE CASH WRAPS/CHECKOUTS (MAINTENANCE FURNITURE)",
    "FURNITURE/FIXTURES STORE INOX/STEEL (MAINTENANCE FURNITURE)",
    "FURNITURE/FIXTURES STORE PLASTIC (MAINTENANCE FURNITURE)",
    "FURNITURE/FIXTURES STORE WOOD (MAINTENANCE FURNITURE)","OTHER (MAINTENANCE FURNITURE)",
    "SHELVING (MAINTENANCE FURNITURE)","(SHELL)FISH PROCESSING MACHINES (MAINTENANCE MACHINERY)",
    "AUDIO/SOUND EQUIPMENT (MAINTENANCE MACHINERY)","BREAD PROCESSING MACHINES (MAINTENANCE MACHINERY)",
    "CHEESE PROCESSING MACHINES (MAINTENANCE MACHINERY)",
    "CLEANING MACHINES/CLEANING DISPENSER (MAINTENANCE MACHINERY)",
    "COFFEE MACHINES (MAINTENANCE MACHINERY)","DELI EQUIPMENT & UTENSILS (MAINTENANCE MACHINERY)",
    "FRUIT & VEG PROCESSING MACHINES (MAINTENANCE MACHINERY)","GRILLS (MAINTENANCE MACHINERY)",
    "MEAT PROCESSING MACHINES (MAINTENANCE MACHINERY)","OTHER (MAINTENANCE MACHINERY)",
    "OVENS (MAINTENANCE MACHINERY)","PACKING MACHINE (MAINTENANCE MACHINERY)",
    "PAPER PROCESSING MACHINES (MAINTENANCE MACHINERY)",
    "REVERSE VENDING MACHINES (MAINTENANCE MACHINERY)","VENDING MACHINES (MAINTENANCE MACHINERY)",
    "WEIGHING EQUIPMENT (MAINTENANCE MACHINERY)","OTHER (MAINTENANCE MERCHANDISING)",
    "SHELVING ACCESSORIES (MAINTENANCE MERCHANDISING)","SHOPPING BASKETS (MAINTENANCE MERCHANDISING)",
    "SHOPPING CARTS/TROLLEYS (MAINTENANCE MERCHANDISING)","SIGNING (MAINTENANCE MERCHANDISING)",
    "ENTRANCE BARRIERS & MECHANICS/SWING GATES (MAINTENANCE SECURITY)",
    "FIRE SAFETY (MAINTENANCE SECURITY)","OTHER (MAINTENANCE SECURITY)",
    "SAFE/MONEY HANDLING (MAINTENANCE SECURITY)","SECURITY SYSTEMS (MAINTENANCE SECURITY)",
    "TELETUBE CHECK OUT AIRBOXSYSTEM (MAINTENANCE SECURITY)","OTHER (MERCHANDISING)",
    "SHELVING ACCESSORIES (MERCHANDISING)","SHOPPING BASKETS (MERCHANDISING)",
    "SHOPPING CARTS/TROLLEYS (MERCHANDISING)","SIGNING (MERCHANDISING)",
    "ENTRANCE BARRIERS & MECHANICS/SWING GATES (SECURITY)","FIRE SAFETY (SECURITY)",
    "OTHER (SECURITY)","SAFE/MONEY HANDLING (SECURITY)","SECURITY SYSTEMS (SECURITY)",
    "TELETUBE CHECK OUT AIRBOXSYSTEM (SECURITY)","CATERING OFFICES/WAREHOUSES",
    "CLEANING & HYGIENE SERVICES","OFFICE CLEANING SERVICES","PEST CONTROL","QUALITY AUDITS",
    "SANITARY SERVICES","STORE CLEANING SERVICES","WAREHOUSE CLEANING","ARCHIVING",
    "OTHER FACILITY SUPPORT SERVICES","SURROUNDINGS SERVICES","FIRE PROTECTION SERVICES",
    "IN-STORE SECURITY","WAREHOUSE AND OFFICE SECURITY","DATACENTER HARDWARE",
    "INFRASTRUCTURE H/W - OTHERS","PRINTING HARDWARE","STORE EQUIPMENT - OTHERS",
    "STORE EQUIPMENT (ELECTRONIC SHELF LABELS)","STORE EQUIPMENT (HANDHELDS)",
    "STORE EQUIPMENT (SCALES)","IT","AMS TESTING SERVICES",
    "APPLICATION MAINTENANCE AND SUPPORT","APPLICATION PROJECT SERVICES",
    "DATA CENTER SERVICES (INFRASTRUCTURE)","DATA CENTER SERVICES (IT 3RD PARTY SERVICES)",
    "END USER COMPUTING","INFRASTRUCTURE OUTSOURCING SERVICES (IT 3RD PARTY SERVICES)",
    "IT BREAK/FIX SERVICES AND MAINTENANCE","OTHER (INFRASTRUCTURE PROJECT SERVICES)",
    "PAY CARDS","PEN TESTING","PRINTED SERVICES (IT)","TESTING AS A SERVICE",
    "EXTERNAL IT PERSONNEL","IT CONSULTING","IT HIRED SERVICES",
    "OTHER IT PROFESSIONAL SERVICES","LICENSE MANAGEMENT","SOFTWARE AS A SERVICE",
    "SOFTWARE LICENSE","SOFTWARE MAINTENANCE","CONFERENCING SERVICES","FIXED TELEPHONY",
    "MOBILE TELEPHONY","OTHER TELECOM SERVICES","TELECOM HARDWARE","WIDE AREA NETWORK",
    "OUTSOURCED AMBIENT","OUTSOURCED CUSTOMS BROKERS","OUTSOURCED E-COM","OUTSOURCED FRESH",
    "OUTSOURCED FROZEN","OUTSOURCED RETURNABLES","HOME DELIVERY TRANSPORT OPERATIONS",
    "INTERNATIONAL INBOUND TRANSPORT OPERATIONS - RAIL TRANSPORT",
    "INTERNATIONAL INBOUND TRANSPORT OPERATIONS - ROAD TRANSPORT",
    "INTERNATIONAL INBOUND TRANSPORT OPERATIONS - SEA TRANSPORT",
    "NATIONAL INBOUND TRANSPORT OPERATIONS","NATIONAL OUTBOUND TRANSPORT",
    "OWNED VEHICLES FLEET","OWNED VEHICLES MAINTENANCE","SMALL PARCELS",
    "BATTERIES FOR MATERIAL HANDLING EQUIPMENT","CRATES","MATERIAL HANDLING EQUIPMENT",
    "MATERIAL HANDLING EQUIPMENT MAINTENANCE","OTHER (WAREHOUSE INVENTORY)","PALLETS",
    "RACKING WAREHOUSE","ROLLING CARRIERS","MECHANIZATION SERVICE & MAINTENANCE",
    "MECHANIZATION SOLUTION","COMMUNICATIONS/ PR","CREATIVE EXECUTION",
    "LOCAL/ STORE EVENTS AND INSTORE ACTIVATIONS","LOYALTY","MONETIZATION",
    "OUTDOOR / INDOOR SIGNAGE","PACKAGING DESIGN","STRATEGIC","(VOICE) ACTORS",
    "FILM/VIDEO PRODUCTION","MUSIC INSTORE","PHOTOGRAPHY","AFFILIATE MARKETING",
    "DIGITAL SIGNAGE","ONLINE MARKETING","SOCIAL MEDIA","WEB & APPS DESIGN",
    "EVENTS (EVENTS)","CONSUMER INSIGHTS","MARKET INSIGHTS","MEDIA AGENCY","ONLINE",
    "OUT OF HOME","PRINT ADVERTISEMENT","RADIO","SEO AND SEA","TV","PUBLICATION PAPER",
    "PRINT MANAGEMENT","PRINT PRODUCTION","PRINT DISTRIBUTION",
    "PRINT DISTRIBUTION QUALITY CHECK","SPONSORING","DONATIONS","EMPLOYEES SOCIAL BENEFITS",
    "HR MEMBERSHIPS","WAGES","LAND DRAINING RATES","LOCAL TAXES","OTHER CHARGES & TAXES",
    "PENALTIES","PROPERTY TAXES","SEWAGE CHARGES","MEMBERSHIPS","INTER COMPANY",
    "FOR RESALE FUEL","INTERCOMPANY","TRADE / FOR RESALE (INTERCOMPANY)",
    "CHAMBER OF COMMERCE",
    "OTHER NGO (NON-GOVERNMENTAL ORGANIZATION) (NGO (NON-GOVERNMETAL ORGANIZATION))",
    "RETAILER ASSOCIATION FEE","NON-NFR","COLLECTION FEES","LEGAL FEES",
    "REAL ESTATE & CONSTRUCTION CHARGES","TRADE / FOR RESALE (NON-NFR SPEND)",
    "OTHER INCOME",
    "OTHER NGO (NON-GOVERNMENTAL ORGANIZATION) (OTHER NGO (NON-GOVERNMENTAL ORGANIZATION))",
    "QUOTATION STOCK EXCHANGE","BAKERY BAGS","BOTTLES & TUBES","CARTON BOXES","CUPS & LIDS",
    "FOILS","INSTORE BAGS AND NETS","LABELS & SLEEVES","PAPER WRAPS & RUBBERS",
    "TRAYS, BOWLS AND PLATTERS","(THERMAL) TILL ROLLS","CLEANING CHEMICALS/MATERIALS",
    "DISPOSABLES","DISTRIBUTION SUPPLIES","GENERAL SUPPLIES","INSTORE SUPPLY PAPER",
    "MEAT DEPT. SUPPLIES","NON-PLASTIC CARRIER BAGS (CHECK OUTS)","OFFICE SUPPLIES",
    "PAPER HYGIENE PRODUCTS","PLASTIC CARRIER BAGS (CHECK OUTS)","PROTECTIVE CLOTHING",
    "QUALITY ASSURANCE SUPPLIES","SHELF LABELS","STORE PROMOTIONAL SUPPLIES","UNIFORMS",
    "ELECTRICITY","PPAs","CAR FUEL","DIESEL FOR STANDBY GENERATORS","FUEL FOR RESALE",
    "SUSTAINABLE FUELS","TRUCK FUEL","HEATING","NATURAL GAS","COLLECTIVE SYSTEMS",
    "EXPIRED MEAT","GENERAL WASTE","GLASS WASTE","METAL WASTE","ORGANIC WASTE",
    "OTHER WASTE","PAPER & CARDBOARD WASTE","PLASTIC & FOIL WASTE",
    "RECYCLING EQUIPMENT BUY OR RENTAL","SANITARY WASTE","WASTE MANAGEMENT","WOOD WASTE","WATER",
]

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_QUERIES  = 2
VALID_SCORES = [15, 45, 70, 98]
RISK_CFG     = {
    15: ("LOW",      "#22c55e", "#052e16", "#16a34a"),
    45: ("MODERATE", "#facc15", "#1c1a00", "#ca8a04"),
    70: ("HIGH",     "#f97316", "#1c0a00", "#ea580c"),
    98: ("CRITICAL", "#ef4444", "#1c0000", "#dc2626"),
}
CHART_COLORS = ["#f97316","#3b82f6","#22c55e","#a855f7","#facc15","#ec4899","#06b6d4","#e11d48"]

# ── Tool schemas ──────────────────────────────────────────────────────────────
TOOL_M1 = {
    "name": "output_cost_analysis",
    "description": "Output structured cost head analysis.",
    "input_schema": {
        "type": "object",
        "properties": {
            "scope_note": {"type": "string"},
            "freshness": {
                "type": "object",
                "properties": {
                    "check_date": {"type": "string"}, "region": {"type": "string"},
                    "tax_basis": {"type": "string"}, "primary_benchmarks": {"type": "string"},
                    "most_recent_source_date": {"type": "string"},
                    "confidence_level": {"type": "string", "enum": ["High","Medium","Low"]},
                    "narrative": {"type": "string"}
                },
                "required": ["check_date","region","tax_basis","primary_benchmarks",
                             "most_recent_source_date","confidence_level","narrative"]
            },
            "cost_heads": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}, "weight_pct": {"type": "number"},
                        "why_included": {"type": "string"}, "best_fit_index": {"type": "string"},
                        "why_index": {"type": "string"}, "is_proxy": {"type": "boolean"}
                    },
                    "required": ["name","weight_pct","why_included","best_fit_index","why_index","is_proxy"]
                },
                "minItems": 4, "maxItems": 6
            }
        },
        "required": ["scope_note","freshness","cost_heads"]
    }
}

TOOL_INFLATION = {
    "name": "output_inflation",
    "description": "Output 6-month inflation impact projection by cost head.",
    "input_schema": {
        "type": "object",
        "properties": {
            "analysis_basis": {"type": "string"},
            "key_assumptions": {"type": "string"},
            "months": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "weighted_total_pct": {"type": "number"},
                        "key_driver": {"type": "string"},
                        "cost_head_impacts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "weight_pct": {"type": "number"},
                                    "projected_change_pct": {"type": "number"},
                                    "direction": {"type": "string", "enum": ["up","down","stable"]},
                                    "driver": {"type": "string"}
                                },
                                "required": ["name","weight_pct","projected_change_pct","direction","driver"]
                            }
                        }
                    },
                    "required": ["label","weighted_total_pct","key_driver","cost_head_impacts"]
                },
                "minItems": 6, "maxItems": 6
            }
        },
        "required": ["analysis_basis","key_assumptions","months"]
    }
}

TOOL_SUPPLY = {
    "name": "output_supply_risk",
    "description": "Output detailed commodity supply risk analysis.",
    "input_schema": {
        "type": "object",
        "properties": {
            "material_service": {"type": "string"},
            "current_supply_risk": {"type": "integer", "enum": [15,45,70,98]},
            "forecasted_supply_risk": {"type": "integer", "enum": [15,45,70,98]},
            "variables": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"},
                        "analysis": {"type": "string"}
                    },
                    "required": ["heading","analysis"]
                },
                "minItems": 4, "maxItems": 6
            },
            "availability_forecast": {
                "type": "object",
                "properties": {
                    "outlook_6m": {
                        "type": "object",
                        "properties": {"heading": {"type": "string"}, "analysis": {"type": "string"}},
                        "required": ["heading","analysis"]
                    },
                    "best_case": {
                        "type": "object",
                        "properties": {"heading": {"type": "string"}, "analysis": {"type": "string"}},
                        "required": ["heading","analysis"]
                    },
                    "base_case": {
                        "type": "object",
                        "properties": {"heading": {"type": "string"}, "analysis": {"type": "string"}},
                        "required": ["heading","analysis"]
                    },
                    "worst_case": {
                        "type": "object",
                        "properties": {"heading": {"type": "string"}, "analysis": {"type": "string"}},
                        "required": ["heading","analysis"]
                    }
                },
                "required": ["outlook_6m","best_case","base_case","worst_case"]
            },
            "additional_comments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"},
                        "analysis": {"type": "string"},
                        "references": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["heading","analysis","references"]
                },
                "minItems": 3, "maxItems": 4
            },
            "all_references": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["material_service","current_supply_risk","forecasted_supply_risk",
                     "variables","availability_forecast","additional_comments","all_references"]
    }
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:#080d16;color:#e5e7eb;}
.stApp{background:#080d16;}
.block-container{padding:0 !important;max-width:100% !important;}
h1,h2,h3{font-family:'DM Sans',sans-serif;color:#f9fafb;}
#MainMenu,footer,header{visibility:hidden;}

.topbar{
  display:flex;justify-content:space-between;align-items:center;
  padding:10px 24px;background:#0a1628;
  border-bottom:1px solid #1e3a5f;
}
.brand{font-weight:700;font-size:1rem;color:#f9fafb;letter-spacing:-0.01em;}
.brand-sub{font-size:0.6rem;color:#4b5563;letter-spacing:0.1em;}
.date-pill{font-size:0.65rem;color:#4b5563;background:rgba(59,130,246,0.08);
  border:1px solid #1e3a5f;border-radius:5px;padding:3px 9px;
  font-family:'DM Mono',monospace;}

.panel{height:calc(100vh - 60px);overflow-y:auto;padding:16px;}
.panel-1{background:#0a1121;border-right:1px solid #1e3a5f;}
.panel-2{background:#080d16;border-right:1px solid #1e3a5f;}
.panel-3{background:#080d16;}

.slabel{font-size:0.6rem;font-weight:700;color:#4b5563;letter-spacing:0.12em;
  text-transform:uppercase;margin-bottom:7px;font-family:'DM Mono',monospace;}
.card{background:#0f172a;border:1px solid #1e3a5f;border-radius:10px;
  padding:14px;margin-bottom:12px;}
.card-sm{background:#0f172a;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;margin-bottom:8px;}

.ch-card{background:#0f172a;border:1px solid #1e3a5f;border-radius:9px;
  padding:12px 14px;margin-bottom:8px;cursor:pointer;transition:border-color 0.15s;}
.ch-card:hover{border-color:#3b82f6;}
.ch-card-active{border:1.5px solid #3b82f6 !important;background:#0a1628 !important;}
.ch-name{font-size:0.7rem;color:#6b7280;text-transform:uppercase;
  letter-spacing:0.1em;margin-bottom:4px;}
.ch-weight{font-size:1.4rem;font-weight:700;color:#f9fafb;line-height:1;}
.ch-index{font-size:0.68rem;color:#4b5563;margin-top:5px;}
.ch-arrow{font-size:0.65rem;color:#4b5563;margin-top:6px;}

.risk-badge{display:inline-block;border-radius:5px;padding:4px 10px;
  font-weight:700;font-size:0.72rem;letter-spacing:0.06em;font-family:'DM Mono',monospace;}
.proxy-tag{display:inline-block;background:rgba(250,204,21,0.1);
  border:1px solid rgba(250,204,21,0.3);border-radius:3px;padding:1px 5px;
  font-size:0.6rem;color:#fde68a;font-family:'DM Mono',monospace;margin-left:4px;}

.bullet{border-left:2px solid #1e3a5f;padding:9px 12px;margin-bottom:9px;
  border-radius:0 6px 6px 0;background:rgba(255,255,255,0.02);}
.bullet-marker{color:#3b82f6;font-weight:700;margin-right:4px;}
.bullet-heading{color:#93c5fd;font-weight:600;font-size:0.82rem;}
.bullet-body{color:#d1d5db;font-size:0.8rem;line-height:1.65;}

.scenario-best{border-left:2px solid #22c55e;padding:9px 12px;
  background:rgba(34,197,94,0.04);border-radius:0 7px 7px 0;margin-bottom:7px;}
.scenario-base{border-left:2px solid #ca8a04;padding:9px 12px;
  background:rgba(250,204,21,0.04);border-radius:0 7px 7px 0;margin-bottom:7px;}
.scenario-worst{border-left:2px solid #dc2626;padding:9px 12px;
  background:rgba(239,68,68,0.04);border-radius:0 7px 7px 0;margin-bottom:7px;}
.sc-label{font-size:0.6rem;font-weight:700;letter-spacing:0.1em;
  margin-bottom:3px;font-family:'DM Mono',monospace;}
.sc-heading{color:#e5e7eb;font-weight:600;font-size:0.79rem;}
.sc-body{color:#9ca3af;font-size:0.78rem;line-height:1.6;margin-top:3px;}

.ref-link{font-size:0.65rem;color:#3b82f6;word-break:break-all;
  line-height:1.8;font-family:'DM Mono',monospace;display:block;}
.conf-high{color:#22c55e;font-weight:700;}
.conf-med{color:#facc15;font-weight:700;}
.conf-low{color:#f97316;font-weight:700;}

.period-btn{display:inline-block;padding:3px 10px;border:1px solid #1e3a5f;
  border-radius:5px;font-size:0.7rem;color:#6b7280;cursor:pointer;
  margin-right:4px;background:#0f172a;}
.period-btn-active{border-color:#3b82f6;color:#93c5fd;background:#0a1628;}

.footer{text-align:center;padding:16px;border-top:1px solid #0f172a;
  font-size:0.65rem;color:#374151;line-height:2;}

div[data-testid="stButton"] button{
  background:linear-gradient(135deg,#1d4ed8,#2563eb);color:#fff;
  font-weight:700;border:none;border-radius:8px;
  padding:0.5rem 1.5rem;font-family:'DM Sans',sans-serif;font-size:0.85rem;}
div[data-testid="stButton"] button:hover{
  background:linear-gradient(135deg,#2563eb,#3b82f6);}
div[data-testid="stButton"] button:disabled{background:#1e3a5f;color:#4b5563;}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def today_str():
    return datetime.today().strftime("%d %B %Y")

def get_api_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        st.error("API key not configured. Go to Streamlit Cloud > Settings > Secrets and add: ANTHROPIC_API_KEY = \"sk-ant-...\"")
        st.stop()

def snap_risk(score):
    try: score = int(float(score))
    except: return 45
    return min(VALID_SCORES, key=lambda x: abs(x - score))

def risk_badge(score):
    score = snap_risk(score)
    label, color, bg, border = RISK_CFG[score]
    return (f'<span class="risk-badge" style="color:{color};background:{bg};border:1.5px solid {border};">' +
            f'● {score} — {label}</span>')

def conf_cls(level):
    l = str(level).lower()
    if "high" in l: return "conf-high"
    if "low"  in l: return "conf-low"
    return "conf-med"

def month_labels_from_today(n=6):
    d = date.today()
    labels = []
    for _ in range(n):
        month = d.month % 12 + 1
        year  = d.year + (1 if d.month == 12 else 0)
        d = d.replace(year=year, month=month, day=1)
        labels.append(d.strftime("%b %Y"))
    return labels

def extract_all_text(response):
    return "\n\n".join(
        b.text.strip() for b in response.content
        if hasattr(b, "type") and b.type == "text"
    )

def extract_tool_result(response, tool_name):
    for b in response.content:
        if hasattr(b, "type") and b.type == "tool_use" and b.name == tool_name:
            return b.input
    raise ValueError(f"Model did not call tool '{tool_name}'. Types returned: {[getattr(b,'type','?') for b in response.content]}")

def _research(client, prompt):
    r = client.messages.create(
        model="claude-opus-4-5", max_tokens=2500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    return extract_all_text(r)

def _structure(client, research_text, tool_def, context_prompt):
    tool_name = tool_def["name"]
    r = client.messages.create(
        model="claude-opus-4-5", max_tokens=2000,
        tools=[tool_def],
        tool_choice={"type": "tool", "name": tool_name},
        messages=[{"role": "user", "content":
            f"Research notes:\n\n{research_text}\n\n{context_prompt}\n\nCall the {tool_name} tool now."}],
    )
    return extract_tool_result(r, tool_name)

# ── Module runners ─────────────────────────────────────────────────────────────
def run_module1(cat, region, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    today  = today_str()
    res = _research(client,
        f"Senior procurement cost analyst. Today is {today}. Research cost structure for: {cat} in {region}. "
        f"Identify 4-6 cost heads (Energy, Raw Materials, Labour, Logistics, Conversion etc.) with weights summing to 100%. "
        f"For each find the best public benchmark index or proxy in {region}. Note confidence level and tax/delivery basis.")
    return _structure(client, res, TOOL_M1,
        f"Structure cost analysis for {cat} in {region}. Set check_date to '{today}'. Weights must sum to 100.")

def run_inflation(cat, region, cost_heads, api_key):
    client  = anthropic.Anthropic(api_key=api_key)
    today   = today_str()
    labels  = month_labels_from_today(6)
    ch_list = ", ".join(f"{c['name']} ({c['weight_pct']}%)" for c in cost_heads)
    res = _research(client,
        f"Senior procurement cost analyst. Today is {today}. "
        f"Research forward price signals for: {cat} in {region}. Cost heads: {ch_list}. "
        f"Find latest futures curves and analyst forecasts for each benchmark. "
        f"Project % change vs current levels for months: {labels}.")
    return _structure(client, res, TOOL_INFLATION,
        f"Structure inflation projection for {cat} in {region}. "
        f"Exactly 6 months: {labels}. "
        f"weighted_total_pct = sum of (projected_change_pct * weight_pct / 100).")

def run_supply_risk(cat, cost_head_name, commodity, region, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    today  = today_str()
    res = _research(client,
        f"Senior procurement supply risk analyst. Today is {today}. "
        f"Research supply risk for commodity: {commodity} (cost head: {cost_head_name} for {cat}) in {region}. "
        f"Find latest data on: production issues, trade flows, import dependence, logistics constraints, "
        f"geopolitical exposure, sanctions, energy input risks, weather impacts, policy changes. "
        f"Provide 6-month outlook and 12-month best/base/worst scenarios. "
        f"Identify 3-4 buyer watchpoints. Include real source URLs.")
    return _structure(client, res, TOOL_SUPPLY,
        f"Structure supply risk for {commodity} ({cat} - {cost_head_name}) in {region}. "
        f"Assign risk scores only from: 15, 45, 70, 98 (15=least, 98=highest). "
        f"Each bullet heading must be SHORT (3-6 words in UPPER CASE). "
        f"Analysis text must be 2-4 specific sentences with figures and dates. "
        f"Include real source URLs in references.")

# ── Chart builder ──────────────────────────────────────────────────────────────
def build_chart(inflation_data, periods):
    months = inflation_data.get("months", [])[:periods]
    if not months:
        return None
    all_heads = [h["name"] for h in months[0].get("cost_head_impacts", [])]
    labels    = [m["label"] for m in months]
    totals    = [round(m.get("weighted_total_pct", 0), 2) for m in months]

    fig = go.Figure()
    for i, head in enumerate(all_heads):
        vals = []
        for m in months:
            for imp in m.get("cost_head_impacts", []):
                if imp["name"] == head:
                    vals.append(round(imp.get("projected_change_pct", 0) * imp.get("weight_pct", 0) / 100, 3))
                    break
            else:
                vals.append(0)
        fig.add_trace(go.Bar(
            name=head, x=labels, y=vals,
            marker_color=CHART_COLORS[i % len(CHART_COLORS)],
            text=[f"{v:+.2f}%" for v in vals],
            textposition="inside", textfont_size=9,
        ))
    fig.add_trace(go.Scatter(
        name="Weighted total", x=labels, y=totals,
        mode="lines+markers+text",
        line=dict(color="#ffffff", width=2, dash="dot"),
        marker=dict(size=7, color="#ffffff"),
        text=[f"{v:+.2f}%" for v in totals],
        textposition="top center", textfont=dict(size=9, color="#ffffff"),
    ))
    fig.update_layout(
        barmode="relative",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0a1121",
        font=dict(family="DM Sans, sans-serif", color="#d1d5db", size=11),
        legend=dict(orientation="h", y=-0.18, font_size=10,
                    bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=20, t=20, b=80),
        height=280,
        xaxis=dict(gridcolor="#1e3a5f", tickfont_size=10),
        yaxis=dict(gridcolor="#1e3a5f", ticksuffix="%",
                   zeroline=True, zerolinecolor="#1e3a5f", tickfont_size=10),
        hoverlabel=dict(bgcolor="#0f172a", bordercolor="#1e3a5f", font_size=11),
    )
    return fig

# ── Display helpers ────────────────────────────────────────────────────────────
def bullet_html(heading, analysis, accent_color="#93c5fd"):
    return (f'<div class="bullet">' +
            f'<div><span class="bullet-marker">&gt;</span>' +
            f'<span class="bullet-heading" style="color:{accent_color};">{heading}:</span></div>' +
            f'<div class="bullet-body">{analysis}</div></div>')

def scenario_html(css_class, label_color, label, heading, analysis):
    return (f'<div class="{css_class}">' +
            f'<div class="sc-label" style="color:{label_color};">{label}</div>' +
            f'<div class="sc-heading">{heading}</div>' +
            f'<div class="sc-body">{analysis}</div></div>')

# ── Session state init ─────────────────────────────────────────────────────────
for k, v in {"query_count": 0, "m1": None, "m_inf": None,
              "m_supply": None, "active_ch": None,
              "last_cat": None, "last_region": None, "periods": 6}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── TOP BAR ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="topbar">' +
    f'<div><div class="brand">&#11203; CommodityPulse</div>' +
    f'<div class="brand-sub">PROCUREMENT INTELLIGENCE PLATFORM</div></div>' +
    f'<div class="date-pill">ANALYSIS DATE: {datetime.today().strftime("%d %b %Y").upper()}</div>' +
    f'</div>', unsafe_allow_html=True)

# ── THREE PANELS ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1.8, 3.2, 4.0])

# ════════════════════════════════════════════════════════════════════════════
# PANEL 1 — Category selector + cost head list
# ════════════════════════════════════════════════════════════════════════════
with col1:
    st.markdown('<div class="panel panel-1">', unsafe_allow_html=True)

    st.markdown('<div class="slabel">L3 Category</div>', unsafe_allow_html=True)
    selected_cat = st.selectbox("cat", CATEGORIES, label_visibility="collapsed",
                                 key="cat_select")

    st.markdown('<div class="slabel" style="margin-top:10px;">Region</div>', unsafe_allow_html=True)
    selected_region = st.selectbox("region",
        ["Europe","North America","Asia Pacific","Middle East & Africa","Latin America"],
        label_visibility="collapsed", key="region_select")

    queries_left = MAX_QUERIES - st.session_state["query_count"]
    ql_html = f'<div style="font-size:0.65rem;color:#4b5563;font-family:DM Mono,monospace;margin:8px 0 4px;">Trial queries: <strong style="color:#f9fafb;">{queries_left}/{MAX_QUERIES}</strong></div>'
    st.markdown(ql_html, unsafe_allow_html=True)

    analyse_btn = st.button("Analyse cost heads →", use_container_width=True,
                             disabled=(queries_left <= 0))

    if st.session_state["m1"] and st.session_state["last_cat"] == selected_cat:
        st.markdown('<div class="slabel" style="margin-top:14px;">Cost Heads — click to drill down</div>',
                    unsafe_allow_html=True)
        cost_heads = st.session_state["m1"].get("cost_heads", [])
        for ch in cost_heads:
            active = (st.session_state["active_ch"] and
                      st.session_state["active_ch"]["name"] == ch["name"])
            card_cls = "ch-card ch-card-active" if active else "ch-card"
            proxy_tag = '<span class="proxy-tag">PROXY</span>' if ch.get("is_proxy") else ""
            arrow = '<div class="ch-arrow">&#9654; viewing analysis</div>' if active else '<div class="ch-arrow">&#9654; click for analysis</div>'
            btn_html = (
                f'<div class="{card_cls}">' +
                f'<div class="ch-name">{ch["name"]}</div>' +
                f'<div class="ch-weight">{ch["weight_pct"]}%</div>' +
                f'<div class="ch-index">{ch["best_fit_index"]}{proxy_tag}</div>' +
                f'{arrow}</div>'
            )
            st.markdown(btn_html, unsafe_allow_html=True)
            if st.button(f"Select {ch['name']}", key=f"ch_{ch['name']}",
                         use_container_width=True):
                st.session_state["active_ch"] = ch
                st.session_state["m_supply"] = None
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PANEL 2 — Supply risk analysis
# ════════════════════════════════════════════════════════════════════════════
with col2:
    st.markdown('<div class="panel panel-2">', unsafe_allow_html=True)

    if st.session_state["active_ch"] and st.session_state["m1"]:
        ch   = st.session_state["active_ch"]
        cat  = st.session_state["last_cat"]
        reg  = st.session_state["last_region"]

        if not st.session_state["m_supply"]:
            with st.spinner(f"Fetching supply risk data for {ch['best_fit_index']}..."):
                try:
                    api_key = get_api_key()
                    st.session_state["m_supply"] = run_supply_risk(
                        cat, ch["name"], ch["best_fit_index"], reg, api_key)
                except Exception as e:
                    st.error(f"Supply risk error: {e}")

        d = st.session_state.get("m_supply")
        if d:
            st.markdown(
                f'<div class="slabel">Supply risk analysis</div>' +
                f'<div style="font-size:1rem;font-weight:700;color:#f9fafb;margin-bottom:3px;">{d.get("material_service", ch["best_fit_index"])}</div>' +
                f'<div style="font-size:0.72rem;color:#6b7280;margin-bottom:12px;">{cat} &rarr; {ch["name"]} ({ch["weight_pct"]}%) &bull; {reg}</div>',
                unsafe_allow_html=True)

            # Risk scores
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f'<div class="card-sm"><div class="slabel">Current supply risk</div>{risk_badge(d["current_supply_risk"])}</div>',
                    unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f'<div class="card-sm"><div class="slabel">Forecasted supply risk</div>{risk_badge(d["forecasted_supply_risk"])}</div>',
                    unsafe_allow_html=True)

            # Variables
            st.markdown('<div class="slabel" style="margin-top:4px;">Variables Impacting Availability</div>', unsafe_allow_html=True)
            html = '<div class="card">'
            for v in d.get("variables", []):
                html += bullet_html(v.get("heading",""), v.get("analysis",""))
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)

            # Availability forecast
            af = d.get("availability_forecast", {})
            st.markdown('<div class="slabel">Availability Forecast</div>', unsafe_allow_html=True)
            html = '<div class="card">'
            html += '<div class="slabel" style="color:#374151;margin-bottom:6px;">6-Month Outlook</div>'
            o6 = af.get("outlook_6m", {})
            html += bullet_html(o6.get("heading","NEXT 6 MONTHS"), o6.get("analysis",""), "#93c5fd")
            html += '<div class="slabel" style="color:#374151;margin-top:10px;margin-bottom:6px;">12-Month Scenarios</div>'
            bc = af.get("best_case", {})
            html += scenario_html("scenario-best",  "#22c55e", "▲ BEST CASE",  bc.get("heading",""), bc.get("analysis",""))
            mc = af.get("base_case", {})
            html += scenario_html("scenario-base",  "#ca8a04", "◆ BASE CASE",  mc.get("heading",""), mc.get("analysis",""))
            wc = af.get("worst_case", {})
            html += scenario_html("scenario-worst", "#dc2626", "▼ WORST CASE", wc.get("heading",""), wc.get("analysis",""))
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)

            # Additional comments
            comments = d.get("additional_comments", [])
            if comments:
                st.markdown('<div class="slabel">Additional Comments</div>', unsafe_allow_html=True)
                html = '<div class="card">'
                for c in comments:
                    refs_html = "".join(
                        f'<a href="{r}" target="_blank" class="ref-link">{r}</a>'
                        for r in c.get("references", []))
                    html += bullet_html(c.get("heading",""), c.get("analysis",""), "#facc15")
                    if refs_html:
                        html += f'<div style="margin-top:4px;padding-left:14px;">{refs_html}</div>'
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)

            # All references
            all_refs = d.get("all_references", [])
            if all_refs:
                with st.expander("All references"):
                    for r in all_refs:
                        st.markdown(f'<a href="{r}" target="_blank" class="ref-link">{r}</a>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;' +
            'height:60vh;color:#374151;text-align:center;">' +
            '<div style="font-size:1.8rem;margin-bottom:10px;">&#9200;</div>' +
            '<div style="font-size:0.9rem;color:#4b5563;">Select a category and click Analyse,<br>' +
            'then click a cost head to see<br>the supply risk analysis here.</div></div>',
            unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PANEL 3 — Weighted inflation impact chart
# ════════════════════════════════════════════════════════════════════════════
with col3:
    st.markdown('<div class="panel panel-3">', unsafe_allow_html=True)

    if st.session_state["m_inf"] and st.session_state["last_cat"] == selected_cat:
        inf = st.session_state["m_inf"]
        cat = st.session_state["last_cat"]
        reg = st.session_state["last_region"]

        st.markdown(
            f'<div class="slabel">Weighted Cost Impact</div>' +
            f'<div style="font-size:1rem;font-weight:700;color:#f9fafb;margin-bottom:3px;">{cat}</div>' +
            f'<div style="font-size:0.72rem;color:#6b7280;margin-bottom:10px;">Inflation projection &bull; {reg}</div>',
            unsafe_allow_html=True)

        # Period selector
        p_cols = st.columns(6)
        periods_choice = st.session_state["periods"]
        for i, n in enumerate([1,2,3,4,5,6]):
            with p_cols[i]:
                if st.button(f"{n}m", key=f"period_{n}", use_container_width=True):
                    st.session_state["periods"] = n
                    st.rerun()

        periods = st.session_state["periods"]
        fig = build_chart(inf, periods)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Breakdown table
        months = inf.get("months", [])[:periods]
        if months:
            all_heads = [h["name"] for h in months[0].get("cost_head_impacts", [])]
            labels    = [m["label"] for m in months]

            th_cells = "".join(f'<th style="text-align:center;padding:5px 7px;color:#4b5563;font-size:0.62rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;">{l}</th>' for l in labels)
            header = (f'<tr><th style="text-align:left;padding:5px 7px;color:#4b5563;font-size:0.62rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;">Cost Head</th>' +
                      f'<th style="text-align:center;padding:5px 7px;color:#4b5563;font-size:0.62rem;font-weight:600;">Wt</th>{th_cells}</tr>')

            rows = ""
            for head in all_heads:
                cells = ""
                wt = 0
                for m in months:
                    for imp in m.get("cost_head_impacts", []):
                        if imp["name"] == head:
                            pct = imp.get("projected_change_pct", 0)
                            wt  = imp.get("weight_pct", 0)
                            try: pct = float(pct)
                            except: pct = 0.0
                            clr = "#f97316" if pct > 0 else ("#22c55e" if pct < 0 else "#6b7280")
                            sign = "+" if pct > 0 else ""
                            cells += f'<td style="text-align:center;padding:5px 7px;color:{clr};font-weight:600;font-family:DM Mono,monospace;font-size:0.72rem;">{sign}{pct:.1f}%</td>'
                            break
                    else:
                        cells += '<td style="text-align:center;padding:5px 7px;color:#4b5563;">—</td>'
                rows += (f'<tr><td style="padding:5px 7px;color:#d1d5db;font-size:0.75rem;">{head}</td>' +
                         f'<td style="text-align:center;padding:5px 7px;color:#6b7280;font-size:0.72rem;font-family:DM Mono,monospace;">{wt}%</td>{cells}</tr>')

            # Totals row
            total_cells = ""
            for m in months:
                t = m.get("weighted_total_pct", 0)
                try: t = float(t)
                except: t = 0.0
                clr = "#f97316" if t > 0 else ("#22c55e" if t < 0 else "#facc15")
                sign = "+" if t > 0 else ""
                total_cells += f'<td style="text-align:center;padding:6px 7px;color:{clr};font-weight:700;font-family:DM Mono,monospace;font-size:0.74rem;">{sign}{t:.2f}%</td>'

            rows += (f'<tr style="background:#0f172a;border-top:1px solid #1e3a5f;">' +
                     f'<td style="padding:6px 7px;color:#f9fafb;font-weight:700;font-size:0.75rem;">Weighted total</td>' +
                     f'<td style="text-align:center;padding:6px 7px;color:#6b7280;font-size:0.72rem;">100%</td>{total_cells}</tr>')

            st.markdown(
                f'<div class="card" style="overflow-x:auto;margin-top:8px;">' +
                f'<div class="slabel" style="margin-bottom:8px;">Monthly breakdown by cost head</div>' +
                f'<table style="width:100%;border-collapse:collapse;">' +
                f'<thead style="border-bottom:1px solid #1e3a5f;">{header}</thead>' +
                f'<tbody>{rows}</tbody></table></div>',
                unsafe_allow_html=True)

        if inf.get("key_assumptions"):
            st.markdown(
                f'<div class="card-sm" style="border-color:rgba(250,204,21,0.25);margin-top:8px;">' +
                f'<div class="slabel">Key Assumptions</div>' +
                f'<div style="font-size:0.75rem;color:#d1d5db;line-height:1.65;">{inf["key_assumptions"]}</div></div>',
                unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.65rem;color:#374151;margin-top:6px;">' +
            f'&#9888; Estimates based on public forward signals as of {today_str()}. Not a financial model.</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;' +
            'height:60vh;color:#374151;text-align:center;">' +
            '<div style="font-size:1.8rem;margin-bottom:10px;">&#128200;</div>' +
            '<div style="font-size:0.9rem;color:#4b5563;">The weighted inflation impact chart<br>' +
            'will appear here after analysis runs.</div></div>',
            unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Run analysis trigger ───────────────────────────────────────────────────────
if analyse_btn:
    api_key = get_api_key()
    st.session_state["query_count"] += 1
    st.session_state.update({"m1": None, "m_inf": None, "m_supply": None,
                              "active_ch": None,
                              "last_cat": selected_cat, "last_region": selected_region})
    with st.spinner(f"Analysing cost structure for {selected_cat}..."):
        try:
            st.session_state["m1"] = run_module1(selected_cat, selected_region, api_key)
        except Exception as e:
            st.error(f"Cost analysis error: {e}")
    if st.session_state["m1"]:
        cost_heads = st.session_state["m1"].get("cost_heads", [])
        with st.spinner("Projecting inflation impact over 6 months..."):
            try:
                st.session_state["m_inf"] = run_inflation(
                    selected_cat, selected_region, cost_heads, api_key)
            except Exception as e:
                st.error(f"Inflation projection error: {e}")
    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">' +
    'CommodityPulse &nbsp;·&nbsp; Procurement Intelligence Platform &nbsp;·&nbsp; ' +
    'Powered by Anthropic Claude with live web search<br>' +
    '<span style="color:#1e3a5f;">&#9670; Ideation &nbsp;/&nbsp; Made &nbsp;/&nbsp; Developed by <strong style="color:#374151;">Ankur Phillips</strong></span>' +
    '</div>',
    unsafe_allow_html=True)
