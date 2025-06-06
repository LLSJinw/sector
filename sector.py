# -*- coding: utf-8 -*-
import streamlit as st
import cohere
import json
import re
import pandas as pd

# Use a secrets.toml file to store your API key
# Example secrets.toml:
# COHERE_API_KEY = "your_cohere_api_key_here"
try:
    co = cohere.Client(st.secrets["COHERE_API_KEY"])
except Exception as e:
    st.error("Cohere API key not found. Please add it to your Streamlit secrets.")
    st.stop()


# --- Static Lists from Thai NCSA ---
NCSA_CII = [
    "กรมการปกครอง", "กรมการแพทย์", "กรมการแพทย์แผนไทยและการแพทย์ทางเลือก", "กรมควบคุมโรค",
    "กรมป้องกันและบรรเทาสาธารณภัย", "กรมวิทยาศาสตร์การแพทย์", "กรมสนับสนุนบริการสุขภาพ", "กรมสุขภาพจิต",
    "กรมอนามัย", "กรมอุตุนิยมวิทยา", "กองการบินทหารเรือ", "กองทะเบียนประวัติอาชญากร", "กองทัพบก",
    "กองทัพเรือ", "กองทัพอากาศ", "กองบัญชาการกองทัพไทย", "กองอำนวยการรักษาความมั่นคงภายในราชอาณาจักร",
    "การท่าเรือแห่งประเทศไทย", "การท่าอากาศยานอู่ตะเภา", "การประปาส่วนภูมิภาค", "การไฟฟ้านครหลวง",
    "การไฟฟ้าฝ่ายผลิตแห่งประเทศไทย", "การไฟฟ้าส่วนภูมิภาค", "การรถไฟฟ้าขนส่งมวลชนแห่งประเทศไทย",
    "การรถไฟแห่งประเทศไทย", "ตลาดหลักทรัพย์แห่งประเทศไทย", "ธนาคารกรุงเทพ", "ธนาคารกรุงไทย",
    "ธนาคารกรุงศรีอยุธยา", "ธนาคารกสิกรไทย", "ธนาคารทหารไทยธนชาต", "ธนาคารไทยพาณิชย์",
    "ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร", "ธนาคารแห่งประเทศไทย", "ธนาคารออมสิน"
]
NCSA_REG = [
    "กรมการขนส่งทางราง", "กรมการปกครอง", "กรมชลประทาน", "กรมศุลกากร", "กระทรวงการคลัง",
    "กระทรวงพลังงาน", "การประปาส่วนภูมิภาค", "ธนาคารแห่งประเทศไทย",
    "สำนักงานการบินพลเรือนแห่งประเทศไทย", "สำนักงานคณะกรรมการกำกับหลักทรัพย์และตลาดหลักทรัพย์",
    "สำนักงานคณะกรรมการกิจการกระจายเสียง กิจการโทรทัศน์ และกิจการโทรคมนาคมแห่งชาติ",
    "สำนักงานคณะกรรรมการอาหารและยา", "สำนักงานตำรวจแห่งชาติ", "สำนักงานปรมาณูเพื่อสันติ",
    "สำนักงานปลัดกระทรวงกลาโหม", "สำนักงานปลัดกระทรวงคมนาคม", "สำนักงานปลัดกระทรวงสาธารณสุข",
    "สำนักงานพัฒนารัฐบาลดิจิทัล (องค์การมหาชน)", "สำนักงานสภาความมั่นคงแห่งชาติ"
]
NCSA_GOV = [
    "กรมการกงสุล", "กรมการขนส่งทางบก", "กรมการข้าว", "มหาวิทยาลัยเกษตรศาสตร์", "กระทรวงศึกษาธิการ",
] + [
    "กรมการค้าต่างประเทศ","กรมการค้าภายใน","กรมการจัดหางาน","กรมการท่องเที่ยว","กรมการเปลี่ยนแปลงสภาพภูมิอากาศและสิ่งแวดล้อม",
    "กรมการพัฒนาชุมชน","กรมการศาสนา","กรมกิจการเด็กและเยาวชน","กรมกิจการผู้สูงอายุ","กรมกิจการสตรีและสถาบันครอบครัว",
]
# Combine all static lists into a single list for easier searching
ALL_STATIC_ORGS = sorted(list(set(NCSA_CII + NCSA_REG + NCSA_GOV)))


# Sector-to-service mapping with compliance and regulator info
SECTOR_DETAILS = {
    "Critical Infrastructure (CII)": {
        "key_services": ["Cyber Risk Assessment (IT/OT)", "Tabletop Exercise (TTX)", "CIRP & Playbook"],
        "secondary_opportunities": ["Gap Assessment", "BCP Alignment"],
        "iso27001_expected": True,
        "regulators": ["สกมช. (NCSA)"],
        "compliance_drivers": ["Cybersecurity Act B.E. 2562", "ISO/IEC 27001"]
    },
    "Regulator": {
        "key_services": ["Cybersecurity Policy Consult", "Regulatory Gap Assessment", "Awareness for Regulators"],
        "secondary_opportunities": ["TTX for National Crisis", "Threat Intelligence Briefing"],
        "iso27001_expected": False,
        "regulators": ["Self-Regulated / Government Oversight"],
        "compliance_drivers": ["Relevant Royal Decrees", "Ministerial Regulations"]
    },
     "Government / SOE": {
        "key_services": ["TTX", "IRP", "Cyber Risk Assessment"],
        "secondary_opportunities": ["Gap Assessment", "อว3/อช3 Consult"],
        "iso27001_expected": False,
        "regulators": ["สพธอ. (ETDA)", "สกมช. (NCSA)"],
        "compliance_drivers": ["Cybersecurity Act B.E. 2562", "Official Information Act B.E. 2540"]
    },
    "Banking / Finance / Insurance (BFSI)": {
        "key_services": ["PDPA Consult", "Pentest", "IRP & Playbook"],
        "secondary_opportunities": ["Source Code Scan", "Awareness Training"],
        "iso27001_expected": True,
        "regulators": ["ธปท. (BOT)", "คปภ. (OIC)"],
        "compliance_drivers": ["Bank of Thailand Cyber Resilience Standards", "OIC Guidelines on Data Protection", "PDPA", "ISO/IEC 27001"]
    },
    "Healthcare": {
        "key_services": ["PDPA Consult", "IRP & TTX"],
        "secondary_opportunities": ["Phishing Simulation", "Awareness Training"],
        "iso27001_expected": False,
        "regulators": ["กระทรวงสาธารณสุข (MOPH)", "สคส. (PDPC)"],
        "compliance_drivers": ["PDPA", "National Health Act B.E. 2550"]
    },
    "Telco / ISP": {
        "key_services": ["Zero Trust Readiness", "CIRP"],
        "secondary_opportunities": ["Gap Assessment", "Managed CSOC"],
        "iso27001_expected": True,
        "regulators": ["กสทช. (NBTC)", "สกมช. (NCSA)"],
        "compliance_drivers": ["NBTC Privacy Requirements", "Cybersecurity Act B.E. 2562"]
    },
    "Software / Tech / SaaS": {
        "key_services": ["Secure SDLC Gap Assessment", "Source Code Scan", "Pentest"],
        "secondary_opportunities": ["Awareness Training", "CI/CD Security"],
        "iso27001_expected": True,
        "regulators": ["สคส. (PDPC)", "สกมช. (NCSA)"],
        "compliance_drivers": ["PDPA", "Secure SDLC Best Practices"]
    },
    "Retail / SME / Logistics": {
        "key_services": ["VA Scan", "PDPA Consult"],
        "secondary_opportunities": ["Awareness Training", "Phishing Simulation"],
        "iso27001_expected": False,
        "regulators": ["สคส. (PDPC)"],
        "compliance_drivers": ["PDPA", "Business Continuity Planning"]
    },
    "Manufacturing / OT-heavy": {
        "key_services": ["Cyber Risk Assessment (IT/OT)", "CIRP"],
        "secondary_opportunities": ["TTX", "Backup/Restore Drill"],
        "iso27001_expected": False,
        "regulators": ["สกมช. (NCSA)"],
        "compliance_drivers": ["Cybersecurity Act B.E. 2562", "Supply Chain Risk Framework"]
    }
}

# New data structure for the compliance mapping table
COMPLIANCE_MAPPING_DATA = [
    {
        "มาตรา (Section)": "มาตรา 13(5)",
        "หัวข้อกฎหมาย (โดยย่อ)": "หน่วยงาน CII ต้องกำหนดมาตรฐานที่เหมาะสมเพื่อรับมือภัยคุกคามไซเบอร์",
        "Cybersecurity Service Mapping": "🔹 NIST CSF Gap Assessment\n🔹 Cybersecurity Maturity Assessment"
    },
    {
        "มาตรา (Section)": "มาตรา 43, 44, 45",
        "หัวข้อกฎหมาย (โดยย่อ)": "หน่วยงานต้องมีนโยบาย มาตรฐาน และแนวทางการป้องกันภัยไซเบอร์ตามแผนของชาติ",
        "Cybersecurity Service Mapping": "🔹 NIST CSF Gap Assessment (Policy & Controls)\n🔹 Baseline Readiness Only"
    },
    {
        "มาตรา (Section)": "มาตรา 54",
        "หัวข้อกฎหมาย (โดยย่อ)": "ประเมินความเสี่ยงและตรวจสอบระบบความมั่นคงไซเบอร์อย่างน้อยปีละครั้ง โดยผู้ประเมินภายใน/ภายนอก",
        "Cybersecurity Service Mapping": "🔹 Cyber Risk Assessment (IT/OT)"
    },
    {
        "มาตรา (Section)": "มาตรา 58",
        "หัวข้อกฎหมาย (โดยย่อ)": "หน่วยงานต้องรับมือกับภัยคุกคามไซเบอร์ โดยต้องประเมินสถานการณ์ ตรวจสอบ ป้องกัน แจ้งเหตุ ฯลฯ",
        "Cybersecurity Service Mapping": "🔹 Cyber Incident Response Plan (IRP)"
    },
    {
        "มาตรา (Section)": "มาตรา 59",
        "หัวข้อกฎหมาย (โดยย่อ)": "สนับสนุนหน่วยงานอื่นในการรับมือภัยไซเบอร์ และแจ้งเตือนเมื่อพบภัย",
        "Cybersecurity Service Mapping": "🔹 CIRP Tabletop Exercise (TTX)"
    }
]


SECTOR_LABELS = list(SECTOR_DETAILS.keys())

PROMPT_INSTRUCTION = f"""
You are a sector classification assistant. Your task is to categorize a company into one of the following sectors based on its name and likely business activities:
{', '.join(SECTOR_LABELS)}

Provide your answer in a JSON format with two keys: "sector" and "reason". The "reason" should be a brief explanation for your choice.

Example:
Company: "Krungthai AXA"
Output:
{{"sector": "Banking / Finance / Insurance (BFSI)", "reason": "The name contains 'Krungthai' and 'AXA', which are strongly associated with banking and insurance."}}
"""

def find_suggestions(keyword):
    """Searches the combined static list for names containing the keyword."""
    if not keyword:
        return []
    keyword_lower = keyword.lower()
    return [org for org in ALL_STATIC_ORGS if keyword_lower in org.lower()]

def classify_statically(entity_name):
    name_lower = entity_name.lower()
    if any(item.lower() in name_lower for item in NCSA_CII):
        return "Critical Infrastructure (CII)"
    if any(item.lower() in name_lower for item in NCSA_REG):
        return "Regulator"
    if any(item.lower() in name_lower for item in NCSA_GOV):
        return "Government / SOE"
    return None

def get_mapped_sector_from_ai_response(ai_sector_name):
    if not ai_sector_name:
        return None
    if ai_sector_name in SECTOR_DETAILS:
        return ai_sector_name
    for key in SECTOR_DETAILS:
        if ai_sector_name.lower() in key.lower():
            return key
    return None

def classify_with_ai(company_name):
    try:
        response_text = co.chat(
            model="command-r-plus",
            message=f"{PROMPT_INSTRUCTION}\nCompany: {company_name}",
            temperature=0.3
        ).text
        cleaned_json_str = re.sub(r"```json|```", "", response_text).strip()
        parsed_json = json.loads(cleaned_json_str)
        raw_ai_sector = parsed_json.get("sector", "").strip()
        mapped_sector = get_mapped_sector_from_ai_response(raw_ai_sector)
        reason = parsed_json.get("reason", "No reason provided by AI.")
        return mapped_sector, reason
    except Exception:
        return None, None

def display_unified_recommendations(sectors):
    # This function remains the same
    key_services = set()
    secondary_opportunities = set()
    compliance_drivers = set()
    regulators = set()

    for sector in sectors:
        if sector in SECTOR_DETAILS:
            details = SECTOR_DETAILS[sector]
            key_services.update(details.get("key_services", []))
            secondary_opportunities.update(details.get("secondary_opportunities", []))
            compliance_drivers.update(details.get("compliance_drivers", []))
            regulators.update(details.get("regulators", []))

    st.markdown("## 🌟 Unified Recommendations")
    st.markdown("Based on the combined analysis of both rule-based and AI classifications.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ✅ Key Services")
        if key_services:
            for svc in sorted(list(key_services)):
                st.markdown(f"- {svc}")
    with col2:
        st.markdown("### 💡 Secondary Opportunities")
        if secondary_opportunities:
            for opt in sorted(list(secondary_opportunities)):
                st.markdown(f"- {opt}")
    
    st.markdown("---")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("### 📋 Compliance Drivers")
        if compliance_drivers:
            for law in sorted(list(compliance_drivers)):
                st.markdown(f"- {law}")
    with col4:
        st.markdown("### 🏩 Sector Regulators")
        if regulators:
            for reg in sorted(list(regulators)):
                st.markdown(f"- {reg}")


def display_compliance_mapping_table():
    st.markdown("### 📑 รายละเอียดข้อกำหนดตาม พ.ร.บ. ไซเบอร์ฯ ที่เกี่ยวข้อง")
    df = pd.DataFrame(COMPLIANCE_MAPPING_DATA)
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- Main App Logic ---
st.set_page_config(page_title="AI Sector + Service Mapper", page_icon="🧠", layout="wide")
st.title("🧠 AI Sector Classifier + Service Recommendations")

# Initialize session state keys for the new interactive flow
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []
if 'org_to_classify' not in st.session_state:
    st.session_state.org_to_classify = None

# --- UI for Search and Suggestions ---
company_input = st.text_input("🔍 Enter a keyword to search for an organization:", key="company_input")

if st.button("Search for Suggestions", key="search_button"):
    st.session_state.org_to_classify = None # Reset previous classification
    st.session_state.suggestions = find_suggestions(company_input)
    if not st.session_state.suggestions and company_input:
        st.info("No matches found in the static lists. You can classify the entered text directly.")

# Display suggestions as clickable buttons
if st.session_state.suggestions:
    st.markdown("---")
    st.markdown("### 📝 Suggestions from Static Lists")
    st.caption("Click an organization to classify, or refine your search.")
    for org in st.session_state.suggestions:
        if st.button(org, key=org):
            st.session_state.org_to_classify = org
            st.session_state.suggestions = []  # Clear suggestions after selection
            st.rerun() # Rerun the script to trigger classification

# Allow direct classification if there's input but no selection yet
if company_input and not st.session_state.org_to_classify and not st.session_state.suggestions:
     st.markdown("---")
     if st.button(f"Classify '{company_input}' directly with AI", key="classify_direct"):
         st.session_state.org_to_classify = company_input
         st.rerun()

# --- Run Classification and Display Results ---
if st.session_state.org_to_classify:
    st.markdown("---")
    st.markdown(f"## 📊 Classification Analysis for: **{st.session_state.org_to_classify}**")

    with st.spinner("Running classification..."):
        static_sector = classify_statically(st.session_state.org_to_classify)
        ai_sector, ai_reason = classify_with_ai(st.session_state.org_to_classify)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📜 Rule-Based (Official)")
        if static_sector:
            st.success(f"**{static_sector}**")
            st.caption("Matched from a predefined NCSA list.")
        else:
            st.warning("**No Match**")
            st.caption("Not found in predefined NCSA lists.")
    
    with col2:
        st.markdown("### 🤖 AI-Based (Characterization)")
        if ai_sector:
            st.info(f"**{ai_sector}**")
            st.caption(f"Reason: {ai_reason}")
        else:
            st.warning("**No AI Classification**")
            st.caption("AI could not determine a sector.")

    st.markdown("---")

    final_sectors = set()
    if static_sector and static_sector in SECTOR_DETAILS:
        final_sectors.add(static_sector)
    if ai_sector and ai_sector in SECTOR_DETAILS:
        final_sectors.add(ai_sector)

    if final_sectors:
        display_unified_recommendations(list(final_sectors))
        
        is_gov_related = any(s in ["Critical Infrastructure (CII)", "Government / SOE", "Regulator"] for s in final_sectors)
        if is_gov_related:
            st.markdown("---")
            display_compliance_mapping_table()
            
    else:
        st.error("Could not determine a valid, mapped sector from any method to provide recommendations.")
