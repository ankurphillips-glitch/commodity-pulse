import streamlit as st
import anthropic
import plotly.graph_objects as go
from datetime import datetime, date

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CommodityPulse",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 349 L3 categories ─────────────────────────────────────────────────────────
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

MAX_QUERIES  = 2
VALID_SCORES = [15, 45, 70, 98]
RISK_CFG     = {
    15: ("LOW",      "#22c55e", "#052e16", "#166534"),
    45: ("MODERATE", "#fbbf24", "#1c1400", "#92400e"),
    70: ("HIGH",     "#fb923c", "#1c0a00", "#c2410c"),
    98: ("CRITICAL", "#f87171", "#1c0000", "#b91c1c"),
}
CHART_COLORS = ["#fb923c","#60a5fa","#4ade80","#c084fc","#fbbf24","#f472b6","#34d399","#f87171"]

# ── Tool schemas (guaranteed-valid JSON via Anthropic tool_use) ───────────────
TOOL_M1 = {
    "name": "output_cost_analysis",
    "description": "Structured cost head analysis output.",
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
                }, "minItems": 4, "maxItems": 6
            }
        },
        "required": ["scope_note","freshness","cost_heads"]
    }
}

TOOL_INFLATION = {
    "name": "output_inflation",
    "description": "Six-month weighted inflation impact projection.",
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
                }, "minItems": 6, "maxItems": 6
            }
        },
        "required": ["analysis_basis","key_assumptions","months"]
    }
}

TOOL_SUPPLY = {
    "name": "output_supply_risk",
    "description": "Detailed commodity supply risk analysis.",
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
                    "properties": {"heading": {"type": "string"}, "analysis": {"type": "string"}},
                    "required": ["heading","analysis"]
                }, "minItems": 4, "maxItems": 6
            },
            "availability_forecast": {
                "type": "object",
                "properties": {
                    "outlook_6m": {"type": "object", "properties": {"heading": {"type": "string"}, "analysis": {"type": "string"}}, "required": ["heading","analysis"]},
                    "best_case":  {"type": "object", "properties": {"heading": {"type": "string"}, "analysis": {"type": "string"}}, "required": ["heading","analysis"]},
                    "base_case":  {"type": "object", "properties": {"heading": {"type": "string"}, "analysis": {"type": "string"}}, "required": ["heading","analysis"]},
                    "worst_case": {"type": "object", "properties": {"heading": {"type": "string"}, "analysis": {"type": "string"}}, "required": ["heading","analysis"]}
                },
                "required": ["outlook_6m","best_case","base_case","worst_case"]
            },
            "additional_comments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"}, "analysis": {"type": "string"},
                        "references": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["heading","analysis","references"]
                }, "minItems": 3, "maxItems": 4
            },
            "all_references": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["material_service","current_supply_risk","forecasted_supply_risk",
                     "variables","availability_forecast","additional_comments","all_references"]
    }
}

# ── CSS — replicates the mockup flat dark design ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

:root {
    --bg:        #0d1117;
    --bg2:       #161b22;
    --bg3:       #1c2230;
    --border:    rgba(255,255,255,0.07);
    --border2:   rgba(255,255,255,0.13);
    --t1:        #f0f6fc;
    --t2:        #8b949e;
    --t3:        #484f58;
    --blue:      #58a6ff;
    --blue-bg:   rgba(88,166,255,0.08);
    --blue-bd:   rgba(88,166,255,0.25);
    --green:     #3fb950;
    --amber:     #d29922;
    --orange:    #d18616;
    --red:       #f85149;
    --radius:    8px;
    --radius-lg: 12px;
    --mono:      'DM Mono', monospace;
    --sans:      'DM Sans', sans-serif;
}

html, body, [class*="css"] { font-family: var(--sans); background: var(--bg); color: var(--t1); }
.stApp { background: var(--bg); }
.block-container { padding: 0 !important; max-width: 100% !important; }
h1,h2,h3 { font-family: var(--sans); color: var(--t1); }
#MainMenu, footer, header { visibility: hidden; }

/* ── top bar ── */
.topbar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 20px; background: var(--bg2);
    border-bottom: 0.5px solid var(--border2);
}
.brand { font-size: 0.9rem; font-weight: 600; color: var(--t1); }
.brand-sub { font-size: 0.58rem; color: var(--t3); letter-spacing: 0.1em; text-transform: uppercase; }
.date-chip {
    font-size: 0.65rem; color: var(--t3); font-family: var(--mono);
    background: var(--blue-bg); border: 0.5px solid var(--blue-bd);
    border-radius: 5px; padding: 3px 9px; letter-spacing: 0.06em;
}

/* ── column dividers ── */
[data-testid="stColumns"] { gap: 0 !important; }
[data-testid="column"]:nth-child(1) { border-right: 0.5px solid var(--border2); }
[data-testid="column"]:nth-child(2) { border-right: 0.5px solid var(--border2); }

/* ── section labels ── */
.lbl {
    font-size: 0.58rem; font-weight: 500; color: var(--t3);
    letter-spacing: 0.1em; text-transform: uppercase;
    font-family: var(--mono); margin-bottom: 6px; display: block;
}

/* ── cards ── */
.card {
    background: var(--bg2); border: 0.5px solid var(--border);
    border-radius: var(--radius-lg); padding: 14px; margin-bottom: 10px;
}
.card-sm {
    background: var(--bg2); border: 0.5px solid var(--border);
    border-radius: var(--radius); padding: 10px 12px; margin-bottom: 8px;
}
.card-amber { border-color: rgba(210,153,34,0.3) !important; }
.card-blue  { border-color: var(--blue-bd) !important; background: var(--blue-bg) !important; }

/* ── cost head cards ── */
.ch-card {
    background: var(--bg2); border: 0.5px solid var(--border);
    border-radius: var(--radius); padding: 12px 14px; margin-bottom: 6px;
}
.ch-card-active { border: 1.5px solid var(--blue) !important; background: var(--bg3) !important; }
.ch-name  { font-size: 0.6rem; color: var(--t3); text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 2px; font-family: var(--mono); }
.ch-wt    { font-size: 1.5rem; font-weight: 500; color: var(--t1); line-height: 1.1; }
.ch-idx   { font-size: 0.65rem; color: var(--t2); margin-top: 4px; }
.ch-hint  { font-size: 0.6rem; color: var(--t3); margin-top: 5px; }
.proxy    {
    display: inline-block; font-size: 0.58rem; font-family: var(--mono);
    background: rgba(210,153,34,0.12); border: 0.5px solid rgba(210,153,34,0.35);
    border-radius: 3px; padding: 1px 5px; color: #d29922; margin-left: 4px;
}

/* ── risk badges ── */
.rb {
    display: inline-block; border-radius: 5px;
    padding: 3px 10px; font-weight: 500; font-size: 0.7rem;
    letter-spacing: 0.05em; font-family: var(--mono);
}

/* ── bullet blocks  ">HEADING: analysis" ── */
.bul {
    border-left: 2px solid var(--border2); padding: 9px 12px;
    margin-bottom: 9px; border-radius: 0 6px 6px 0;
    background: rgba(255,255,255,0.02);
}
.bul-h { font-size: 0.78rem; font-weight: 500; color: var(--blue); }
.bul-b { font-size: 0.78rem; color: var(--t2); line-height: 1.65; margin-top: 3px; }

/* ── scenario strips ── */
.sc-best  { border-left: 2px solid var(--green);  padding: 9px 12px; background: rgba(63,185,80,0.04);  border-radius: 0 7px 7px 0; margin-bottom: 7px; }
.sc-base  { border-left: 2px solid var(--amber);  padding: 9px 12px; background: rgba(210,153,34,0.04); border-radius: 0 7px 7px 0; margin-bottom: 7px; }
.sc-worst { border-left: 2px solid var(--red);    padding: 9px 12px; background: rgba(248,81,73,0.04);  border-radius: 0 7px 7px 0; margin-bottom: 7px; }
.sc-lbl   { font-size: 0.58rem; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; font-family: var(--mono); margin-bottom: 2px; }
.sc-h     { font-size: 0.8rem; font-weight: 500; color: var(--t1); }
.sc-b     { font-size: 0.77rem; color: var(--t2); line-height: 1.6; margin-top: 3px; }

/* ── refs ── */
.ref { font-size: 0.62rem; color: var(--blue); word-break: break-all; line-height: 1.9; font-family: var(--mono); display: block; }

/* ── Streamlit widget overrides ── */
div[data-testid="stButton"] > button {
    background: var(--bg2) !important;
    border: 0.5px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    color: var(--t1) !important;
    font-family: var(--sans) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1rem !important;
    width: 100% !important;
    transition: border-color 0.15s !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: var(--blue) !important;
    color: var(--blue) !important;
}
/* Primary analyse button */
div[data-testid="stButton"].analyse-btn > button {
    background: var(--blue-bg) !important;
    border-color: var(--blue) !important;
    color: var(--blue) !important;
}
/* Period toggle buttons */
.period-active > button {
    border-color: var(--blue) !important;
    color: var(--blue) !important;
    background: var(--blue-bg) !important;
}
.stSelectbox label { display: none; }
[data-testid="stSelectbox"] > div > div {
    background: var(--bg2) !important;
    border: 0.5px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    color: var(--t1) !important;
    font-size: 0.82rem !important;
}
.stSelectbox svg { color: var(--t2) !important; }
.stExpander { background: var(--bg2); border: 0.5px solid var(--border); border-radius: var(--radius); }
.stExpander summary { font-size: 0.75rem; color: var(--t2); font-family: var(--mono); }

/* ── divider ── */
hr.cp { border: none; border-top: 0.5px solid var(--border2); margin: 14px 0; }
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

def snap_risk(v):
    try: v = int(float(v))
    except: return 45
    return min(VALID_SCORES, key=lambda x: abs(x - v))

def risk_badge(score):
    score = snap_risk(score)
    label, fg, bg, bd = RISK_CFG[score]
    return f'<span class="rb" style="color:{fg};background:{bg};border:1px solid {bd};">&#9679; {score} — {label}</span>'

def conf_color(level):
    l = str(level).lower()
    if "high" in l: return "#3fb950"
    if "low"  in l: return "#f85149"
    return "#d29922"

def month_labels(n=6):
    d = date.today()
    out = []
    for _ in range(n):
        m = d.month % 12 + 1
        y = d.year + (1 if d.month == 12 else 0)
        d = d.replace(year=y, month=m, day=1)
        out.append(d.strftime("%b %Y"))
    return out

def extract_all_text(response):
    return "\n\n".join(
        b.text.strip() for b in response.content
        if hasattr(b, "type") and b.type == "text"
    )

def extract_tool(response, name):
    for b in response.content:
        if hasattr(b, "type") and b.type == "tool_use" and b.name == name:
            return b.input
    types = [getattr(b, "type", "?") for b in response.content]
    raise ValueError(f"Tool '{name}' not called. Got: {types}")

def research(client, prompt):
    r = client.messages.create(
        model="claude-opus-4-5", max_tokens=2500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    return extract_all_text(r)

def structure(client, notes, tool, context):
    name = tool["name"]
    r = client.messages.create(
        model="claude-opus-4-5", max_tokens=2000,
        tools=[tool],
        tool_choice={"type": "tool", "name": name},
        messages=[{"role": "user", "content":
            f"Research notes:\n\n{notes}\n\n{context}\n\nCall {name} now."}],
    )
    return extract_tool(r, name)

# ── Module runners ─────────────────────────────────────────────────────────────
def run_m1(cat, region, api_key):
    c = anthropic.Anthropic(api_key=api_key)
    t = today_str()
    n = research(c, f"Today is {t}. Research cost structure for: {cat} in {region}. "
        "Identify 4-6 cost heads (Energy, Raw Materials, Labour, Logistics, Conversion etc.) summing to 100%. "
        "For each find the best public benchmark or proxy. Note confidence level and tax/delivery basis.")
    return structure(c, n, TOOL_M1,
        f"Structure cost analysis for {cat} in {region}. check_date = '{t}'. Weights must sum to 100.")

def run_inflation(cat, region, cost_heads, api_key):
    c = anthropic.Anthropic(api_key=api_key)
    t = today_str()
    labels = month_labels(6)
    ch_list = ", ".join(f"{h['name']} ({h['weight_pct']}%)" for h in cost_heads)
    n = research(c, f"Today is {t}. Research forward price signals for: {cat} in {region}. "
        f"Cost heads: {ch_list}. Find latest futures/forecasts for each benchmark. "
        f"Project % change vs current for months: {labels}.")
    return structure(c, n, TOOL_INFLATION,
        f"Structure inflation projection for {cat} in {region}. "
        f"Exactly 6 months: {labels}. "
        f"weighted_total_pct = sum of (projected_change_pct * weight_pct / 100).")

def run_supply(cat, ch_name, commodity, region, api_key):
    c = anthropic.Anthropic(api_key=api_key)
    t = today_str()
    n = research(c, f"Today is {t}. Research supply risk for commodity: {commodity} "
        f"(cost head: {ch_name} for {cat}) in {region}. "
        "Find latest: production issues, trade flows, import dependence, logistics, "
        "geopolitical risks, sanctions, energy input, weather, policy changes. "
        "Give 6-month outlook and 12-month best/base/worst. Identify 3-4 buyer watchpoints. "
        "Include real source URLs.")
    return structure(c, n, TOOL_SUPPLY,
        f"Structure supply risk for {commodity} ({cat}/{ch_name}) in {region}. "
        "Risk scores ONLY from: 15, 45, 70, 98. "
        "Each heading: 3-6 words, UPPER CASE. Analysis: 2-4 factual sentences with figures.")

# ── Chart builder ──────────────────────────────────────────────────────────────
def build_chart(inf_data, periods):
    try:
        months = inf_data.get("months", [])
        if not months:
            return None
        months = months[:periods]
        labels  = [m.get("label", f"Month {i+1}") for i, m in enumerate(months)]
        totals  = [float(m.get("weighted_total_pct", 0)) for m in months]
        heads   = [h["name"] for h in months[0].get("cost_head_impacts", [])]

        fig = go.Figure()
        for i, head in enumerate(heads):
            vals = []
            for m in months:
                match = next((h for h in m.get("cost_head_impacts", []) if h["name"] == head), None)
                if match:
                    try:
                        pct = float(match.get("projected_change_pct", 0))
                        wt  = float(match.get("weight_pct", 0))
                        vals.append(round(pct * wt / 100, 3))
                    except:
                        vals.append(0)
                else:
                    vals.append(0)
            fig.add_trace(go.Bar(
                name=head, x=labels, y=vals,
                marker_color=CHART_COLORS[i % len(CHART_COLORS)],
                text=[f"{v:+.2f}%" for v in vals],
                textposition="inside", textfont=dict(size=9, color="#ffffff"),
                hovertemplate=f"<b>{head}</b><br>%{{x}}: %{{y:+.2f}}%<extra></extra>",
            ))
        fig.add_trace(go.Scatter(
            name="Weighted total", x=labels, y=[round(t, 2) for t in totals],
            mode="lines+markers",
            line=dict(color="#f0f6fc", width=1.5, dash="dot"),
            marker=dict(size=6, color="#f0f6fc", symbol="circle"),
            text=[f"{t:+.2f}%" for t in totals],
            textposition="top center", textfont=dict(size=9, color="#f0f6fc"),
            hovertemplate="<b>Weighted total</b><br>%{x}: %{y:+.2f}%<extra></extra>",
        ))
        fig.update_layout(
            barmode="relative",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161b22",
            font=dict(family="DM Sans, sans-serif", color="#8b949e", size=11),
            legend=dict(orientation="h", y=-0.22, font_size=10,
                        bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
            margin=dict(l=36, r=10, t=10, b=80), height=270,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont_size=10),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", ticksuffix="%",
                       zeroline=True, zerolinecolor="rgba(255,255,255,0.1)", tickfont_size=10),
            hoverlabel=dict(bgcolor="#161b22", bordercolor="#30363d", font_size=11),
        )
        return fig
    except Exception as e:
        st.caption(f"Chart error: {e}")
        return None

# ── HTML helpers ──────────────────────────────────────────────────────────────
def bullet(heading, analysis, heading_color="#58a6ff"):
    return (f'<div class="bul">' +
            f'<div class="bul-h" style="color:{heading_color};">&gt; {heading}:</div>' +
            f'<div class="bul-b">{analysis}</div></div>')

def scenario(cls, lbl_color, lbl, heading, analysis):
    return (f'<div class="{cls}">' +
            f'<div class="sc-lbl" style="color:{lbl_color};">{lbl}</div>' +
            f'<div class="sc-h">{heading}</div>' +
            f'<div class="sc-b">{analysis}</div></div>')

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {"qc": 0, "m1": None, "m_inf": None, "m_sup": None,
              "active_ch": None, "last_cat": None, "last_reg": None, "periods": 6}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="topbar">' +
    f'<div><span class="brand">&#11203; CommodityPulse</span>' +
    f'<div class="brand-sub">Procurement Intelligence Platform</div></div>' +
    f'<span class="date-chip">Analysis date: {datetime.today().strftime("%d %b %Y").upper()}</span>' +
    f'</div>', unsafe_allow_html=True)

# ── Three columns — NOTE: NO HTML panel div wrappers. All widgets render directly. ──
col1, col2, col3 = st.columns([1.9, 3.3, 4.0])

# ═══════════════════════════════════════════════════════════════════
# PANEL 1 — Category selector + cost head list
# ═══════════════════════════════════════════════════════════════════
with col1:
    st.markdown("<div style='padding:14px 14px 0;'>", unsafe_allow_html=True)

    st.markdown('<span class="lbl">L3 Category</span>', unsafe_allow_html=True)
    selected_cat = st.selectbox("cat", CATEGORIES, label_visibility="collapsed", key="cat_sel")

    st.markdown('<span class="lbl" style="margin-top:10px;display:block;">Region</span>', unsafe_allow_html=True)
    selected_reg = st.selectbox("reg",
        ["Europe","North America","Asia Pacific","Middle East & Africa","Latin America"],
        label_visibility="collapsed", key="reg_sel")

    ql = MAX_QUERIES - st.session_state["qc"]
    st.markdown(
        f'<span class="lbl" style="margin-top:10px;display:block;">' +
        f'Trial queries remaining: <strong style="color:#f0f6fc;">{ql}/{MAX_QUERIES}</strong></span>',
        unsafe_allow_html=True)
    analyse_btn = st.button("Analyse cost heads &#8594;", use_container_width=True, disabled=(ql <= 0))

    if st.session_state["m1"] and st.session_state["last_cat"] == selected_cat:
        st.markdown('<hr class="cp"><span class="lbl">Cost heads — click to drill down</span>', unsafe_allow_html=True)
        for ch in st.session_state["m1"].get("cost_heads", []):
            active = (st.session_state["active_ch"] and
                      st.session_state["active_ch"]["name"] == ch["name"])
            card_cls = "ch-card ch-card-active" if active else "ch-card"
            proxy_tag = '<span class="proxy">PROXY</span>' if ch.get("is_proxy") else ""
            hint = "&#9654; viewing analysis" if active else "&#9654; click for analysis"
            st.markdown(
                f'<div class="{card_cls}">' +
                f'<div class="ch-name">{ch["name"]}</div>' +
                f'<div class="ch-wt">{ch["weight_pct"]}%</div>' +
                f'<div class="ch-idx">{ch["best_fit_index"]}{proxy_tag}</div>' +
                f'<div class="ch-hint">{hint}</div></div>',
                unsafe_allow_html=True)
            if st.button(f"Select {ch['name']}", key=f"ch_{ch['name']}", use_container_width=True):
                st.session_state["active_ch"] = ch
                st.session_state["m_sup"] = None
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# PANEL 2 — Supply risk analysis
# ═══════════════════════════════════════════════════════════════════
with col2:
    st.markdown("<div style='padding:14px;'>", unsafe_allow_html=True)

    if st.session_state["active_ch"] and st.session_state["m1"]:
        ch  = st.session_state["active_ch"]
        cat = st.session_state["last_cat"]
        reg = st.session_state["last_reg"]

        if not st.session_state["m_sup"]:
            with st.spinner(f"Fetching supply risk data for {ch['best_fit_index']}..."):
                try:
                    st.session_state["m_sup"] = run_supply(
                        cat, ch["name"], ch["best_fit_index"], reg, get_api_key())
                except Exception as e:
                    st.error(f"Supply risk error: {e}")

        d = st.session_state.get("m_sup")
        if d:
            st.markdown(
                '<span class="lbl">Supply Risk Analysis</span>' +
                f'<div style="font-size:1.05rem;font-weight:500;color:#f0f6fc;margin-bottom:2px;">{d.get("material_service", ch["best_fit_index"])}</div>' +
                f'<div style="font-size:0.7rem;color:#484f58;margin-bottom:12px;">{cat} &#8594; {ch["name"]} ({ch["weight_pct"]}%) &bull; {reg}</div>',
                unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f'<div class="card-sm"><span class="lbl">Current Supply Risk</span>{risk_badge(d["current_supply_risk"])}</div>',
                    unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f'<div class="card-sm"><span class="lbl">Forecasted Supply Risk</span>{risk_badge(d["forecasted_supply_risk"])}</div>',
                    unsafe_allow_html=True)

            st.markdown('<span class="lbl" style="margin-top:4px;display:block;">Variables Impacting Availability</span>', unsafe_allow_html=True)
            html = '<div class="card">'
            for v in d.get("variables", []):
                html += bullet(v.get("heading",""), v.get("analysis",""))
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)

            af = d.get("availability_forecast", {})
            st.markdown('<span class="lbl" style="display:block;">Availability Forecast</span>', unsafe_allow_html=True)
            html = '<div class="card">'
            html += '<span class="lbl" style="color:#30363d;">6-Month Outlook</span>'
            o = af.get("outlook_6m", {})
            html += bullet(o.get("heading","NEXT 6 MONTHS"), o.get("analysis",""))
            html += '<span class="lbl" style="color:#30363d;margin-top:10px;display:block;">12-Month Scenarios</span>'
            bc = af.get("best_case",  {})
            mc = af.get("base_case",  {})
            wc = af.get("worst_case", {})
            html += scenario("sc-best",  "#3fb950", "&#9650; BEST CASE",  bc.get("heading",""), bc.get("analysis",""))
            html += scenario("sc-base",  "#d29922", "&#9670; BASE CASE",  mc.get("heading",""), mc.get("analysis",""))
            html += scenario("sc-worst", "#f85149", "&#9660; WORST CASE", wc.get("heading",""), wc.get("analysis",""))
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)

            comments = d.get("additional_comments", [])
            if comments:
                st.markdown('<span class="lbl" style="display:block;">Additional Comments</span>', unsafe_allow_html=True)
                html = '<div class="card">'
                for cm in comments:
                    html += bullet(cm.get("heading",""), cm.get("analysis",""), "#fbbf24")
                    refs = cm.get("references", [])
                    if refs:
                        html += "".join(f'<a href="{r}" target="_blank" class="ref">{r}</a>' for r in refs)
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)

            all_refs = d.get("all_references", [])
            if all_refs:
                with st.expander("All references"):
                    for r in all_refs:
                        st.markdown(f'<a href="{r}" target="_blank" class="ref">{r}</a>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;' +
            'height:65vh;text-align:center;">' +
            '<div style="font-size:1.6rem;margin-bottom:10px;color:#30363d;">&#9200;</div>' +
            '<div style="font-size:0.82rem;color:#484f58;line-height:1.7;">Select a category and click<br>Analyse, then click a cost<br>head to see the supply risk<br>analysis here.</div></div>',
            unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# PANEL 3 — Weighted inflation impact chart
# ═══════════════════════════════════════════════════════════════════
with col3:
    st.markdown("<div style='padding:14px;'>", unsafe_allow_html=True)

    inf = st.session_state.get("m_inf")
    cat = st.session_state.get("last_cat","")
    reg = st.session_state.get("last_reg","Europe")

    if inf and st.session_state["last_cat"] == selected_cat:
        st.markdown(
            '<span class="lbl">Weighted Cost Impact</span>' +
            f'<div style="font-size:1.05rem;font-weight:500;color:#f0f6fc;margin-bottom:1px;">{cat}</div>' +
            f'<div style="font-size:0.7rem;color:#484f58;margin-bottom:12px;">Inflation projection &bull; {reg}</div>',
            unsafe_allow_html=True)

        # Period selector — 6 equal columns
        p_cols = st.columns(6)
        for i, n in enumerate([1,2,3,4,5,6]):
            with p_cols[i]:
                if st.button(f"{n}m", key=f"p{n}", use_container_width=True):
                    st.session_state["periods"] = n
                    st.rerun()

        periods = st.session_state["periods"]

        # Chart
        fig = build_chart(inf, periods)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Chart data unavailable. See breakdown table below.")

        # Breakdown table
        months = inf.get("months", [])[:periods]
        if months:
            heads  = [h["name"] for h in months[0].get("cost_head_impacts", [])]
            labels = [m.get("label","") for m in months]

            def td(val, bold=False, color=None):
                sty = f"color:{color};" if color else ""
                sty += "font-weight:600;" if bold else ""
                sty += "font-family:DM Mono,monospace;" if bold or color else ""
                return f'<td style="padding:5px 8px;font-size:0.72rem;text-align:center;border-bottom:0.5px solid rgba(255,255,255,0.04);{sty}">{val}</td>'

            th_labels = "".join(
                f'<th style="padding:5px 8px;font-size:0.6rem;text-align:center;color:#484f58;font-family:DM Mono,monospace;font-weight:500;text-transform:uppercase;letter-spacing:0.07em;">{l}</th>'
                for l in labels)
            table = (
                '<table style="width:100%;border-collapse:collapse;margin-top:6px;">' +
                f'<thead><tr><th style="text-align:left;padding:5px 8px;font-size:0.6rem;color:#484f58;font-family:DM Mono,monospace;font-weight:500;text-transform:uppercase;">Cost Head</th>' +
                f'<th style="text-align:center;padding:5px 8px;font-size:0.6rem;color:#484f58;font-family:DM Mono,monospace;font-weight:500;">Wt</th>{th_labels}</tr></thead><tbody>'
            )
            for head in heads:
                wt = 0
                cells = ""
                for m in months:
                    imp = next((h for h in m.get("cost_head_impacts", []) if h["name"] == head), None)
                    if imp:
                        wt = imp.get("weight_pct", 0)
                        try: pct = float(imp.get("projected_change_pct", 0))
                        except: pct = 0.0
                        clr = "#fb923c" if pct > 0 else ("#4ade80" if pct < 0 else "#484f58")
                        sign = "+" if pct > 0 else ""
                        cells += td(f"{sign}{pct:.1f}%", bold=True, color=clr)
                    else:
                        cells += td("—")
                table += (f'<tr><td style="padding:5px 8px;font-size:0.75rem;color:#f0f6fc;border-bottom:0.5px solid rgba(255,255,255,0.04);">{head}</td>' +
                          f'<td style="padding:5px 8px;font-size:0.7rem;text-align:center;color:#484f58;font-family:DM Mono,monospace;border-bottom:0.5px solid rgba(255,255,255,0.04);">{wt}%</td>{cells}</tr>')

            # Totals row
            total_cells = ""
            for m in months:
                try: t = float(m.get("weighted_total_pct", 0))
                except: t = 0.0
                clr  = "#fb923c" if t > 0 else ("#4ade80" if t < 0 else "#fbbf24")
                sign = "+" if t > 0 else ""
                total_cells += f'<td style="padding:6px 8px;font-size:0.74rem;text-align:center;font-weight:600;font-family:DM Mono,monospace;color:{clr};">{sign}{t:.2f}%</td>'

            table += (
                '<tr style="background:rgba(88,166,255,0.06);border-top:0.5px solid rgba(255,255,255,0.1);">' +
                '<td style="padding:6px 8px;font-size:0.75rem;font-weight:500;color:#f0f6fc;">Weighted total</td>' +
                f'<td style="padding:6px 8px;font-size:0.7rem;text-align:center;color:#484f58;font-family:DM Mono,monospace;">100%</td>{total_cells}</tr>' +
                '</tbody></table>'
            )
            st.markdown(f'<div class="card" style="overflow-x:auto;">{table}</div>', unsafe_allow_html=True)

        if inf.get("key_assumptions"):
            st.markdown(
                f'<div class="card card-amber" style="margin-top:8px;">' +
                f'<span class="lbl">Key Assumptions</span>' +
                f'<div style="font-size:0.75rem;color:#8b949e;line-height:1.65;">{inf["key_assumptions"]}</div></div>',
                unsafe_allow_html=True)

        st.markdown(
            f'<div style="font-size:0.62rem;color:#30363d;margin-top:6px;">' +
            f'Estimates based on public forward signals as of {today_str()}. Not a financial model.</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;' +
            'height:65vh;text-align:center;">' +
            '<div style="font-size:1.6rem;margin-bottom:10px;color:#30363d;">&#128200;</div>' +
            '<div style="font-size:0.82rem;color:#484f58;line-height:1.7;">The weighted inflation<br>impact chart will appear<br>here after analysis runs.</div></div>',
            unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── Analyse trigger ───────────────────────────────────────────────────────────
if analyse_btn:
    api_key = get_api_key()
    st.session_state.update({"qc": st.session_state["qc"] + 1,
                              "m1": None, "m_inf": None, "m_sup": None,
                              "active_ch": None,
                              "last_cat": selected_cat, "last_reg": selected_reg})
    with st.spinner(f"Analysing cost structure for {selected_cat}..."):
        try:
            st.session_state["m1"] = run_m1(selected_cat, selected_reg, api_key)
        except Exception as e:
            st.error(f"Cost analysis error: {e}")
    if st.session_state["m1"]:
        with st.spinner("Projecting 6-month inflation impact..."):
            try:
                st.session_state["m_inf"] = run_inflation(
                    selected_cat, selected_reg,
                    st.session_state["m1"].get("cost_heads", []), api_key)
            except Exception as e:
                st.error(f"Inflation projection error: {e}")
    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;padding:14px 0;border-top:0.5px solid rgba(255,255,255,0.06);' +
    'font-size:0.62rem;color:#30363d;line-height:2.2;">' +
    'CommodityPulse &nbsp;&middot;&nbsp; Procurement Intelligence Platform &nbsp;&middot;&nbsp;' +
    ' Powered by Anthropic Claude with live web search<br>' +
    '<span style="color:#21262d;">&#9670; Ideation &nbsp;/&nbsp; Made &nbsp;/&nbsp; Developed by ' +
    '<strong style="color:#30363d;">Ankur Phillips</strong></span></div>',
    unsafe_allow_html=True)
