import streamlit as st
import cohere
import json
import re

# Initialize Cohere Chat model with your API key
co = cohere.Client("sNIAP0wwbfOagyZr75up0a6tVejuZ6ONH0ODCsOa")

# Sector-to-service mapping with compliance and regulator info
SECTOR_DETAILS = {
    "Critical Infrastructure (CII)": {
        "key_services": ["Cyber Risk Assessment (IT/OT)", "Tabletop Exercise (TTX)", "CIRP & Playbook"],
        "secondary_opportunities": ["Gap Assessment", "BCP Alignment"],
        "iso27001_expected": True,
        "regulators": ["NCSA"],
        "compliance_drivers": ["Cybersecurity Act B.E. 2562", "ISO/IEC 27001"]
    },
    "Banking / Finance / Insurance (BFSI)": {
        "key_services": ["PDPA Consult", "Pentest", "IRP & Playbook"],
        "secondary_opportunities": ["Source Code Scan", "Awareness Training"],
        "iso27001_expected": True,
        "regulators": ["BOT", "OIC"],
        "compliance_drivers": ["Bank of Thailand Cyber Resilience Standards", "OIC Guidelines on Data Protection", "PDPA", "ISO/IEC 27001"]
    },
    "Healthcare": {
        "key_services": ["PDPA Consult", "IRP & TTX"],
        "secondary_opportunities": ["Phishing Simulation", "Awareness Training"],
        "iso27001_expected": False,
        "regulators": ["MOPH", "PDPC"],
        "compliance_drivers": ["PDPA", "National Health Act B.E. 2550"]
    },
    "Government / SOE": {
        "key_services": ["TTX", "IRP", "Cyber Risk Assessment"],
        "secondary_opportunities": ["Gap Assessment", "อว3/อช3 Consult"],
        "iso27001_expected": False,
        "regulators": ["ETDA", "NCSA"],
        "compliance_drivers": ["Cybersecurity Act B.E. 2562", "Official Information Act B.E. 2540"]
    },
    "Telco / ISP": {
        "key_services": ["Zero Trust Readiness", "CIRP"],
        "secondary_opportunities": ["Gap Assessment", "Managed CSOC"],
        "iso27001_expected": True,
        "regulators": ["NBTC", "NCSA"],
        "compliance_drivers": ["NBTC Privacy Requirements", "Cybersecurity Act B.E. 2562"]
    },
    "Software / Tech / SaaS": {
        "key_services": ["Secure SDLC Gap Assessment", "Source Code Scan", "Pentest"],
        "secondary_opportunities": ["Awareness Training", "CI/CD Security"],
        "iso27001_expected": True,
        "regulators": ["PDPC", "NCSA"],
        "compliance_drivers": ["PDPA", "Secure SDLC Best Practices"]
    },
    "Retail / SME / Logistics": {
        "key_services": ["VA Scan", "PDPA Consult"],
        "secondary_opportunities": ["Awareness Training", "Phishing Simulation"],
        "iso27001_expected": False,
        "regulators": ["PDPC"],
        "compliance_drivers": ["PDPA", "Business Continuity Planning"]
    },
    "Manufacturing / OT-heavy": {
        "key_services": ["Cyber Risk Assessment (IT/OT)", "CIRP"],
        "secondary_opportunities": ["TTX", "Backup/Restore Drill"],
        "iso27001_expected": False,
        "regulators": ["NCSA"],
        "compliance_drivers": ["Cybersecurity Act B.E. 2562", "Supply Chain Risk Framework"]
    }
}

SECTOR_LABELS = list(SECTOR_DETAILS.keys())

PROMPT_INSTRUCTION = f"""
You're a sector classification assistant trained to categorize companies into one of the following sectors:

{', '.join(SECTOR_LABELS)}

Given a company name, return the sector only, and a brief reason in JSON format.

Example output:
{{"sector": "Healthcare", "reason": "The company operates a hospital and healthtech systems."}}
"""

def classify_sector_with_chat(company_name):
    try:
        response = co.chat(
            model="command-r-plus",
            message=f"{PROMPT_INSTRUCTION}\nCompany: {company_name}",
            temperature=0.3
        )
        return response.text
    except Exception as e:
        return None, str(e)

# --- Streamlit UI ---
st.set_page_config(page_title="AI Sector + Service Mapper", page_icon="🧠")
st.title("🧠 AI Sector Classifier + Service Recommendations")

company_input = st.text_input("🔍 Enter customer or organization name:")

if company_input:
    with st.spinner("Classifying sector via Cohere..."):
        result = classify_sector_with_chat(company_input)

    if result:
        st.success("✅ Sector Classification Result")
        st.code(result, language="json")

        try:
            cleaned = re.sub(r"```json|```", "", result).strip()
            parsed = json.loads(cleaned)
            sector = parsed.get("sector", "").strip()
            reason = parsed.get("reason", "")

            if sector in SECTOR_DETAILS:
                details = SECTOR_DETAILS[sector]

                st.markdown(f"### 🏷️ Sector: **{sector}**")
                st.markdown(f"📌 **Reason:** {reason}")
                st.markdown("### ✅ Key Services")
                for svc in details["key_services"]:
                    st.markdown(f"- {svc}")
                st.markdown("### 💡 Secondary Opportunities")
                for opt in details["secondary_opportunities"]:
                    st.markdown(f"- {opt}")
                st.markdown("### 📋 Compliance Drivers")
                for law in details.get("compliance_drivers", []):
                    st.markdown(f"- {law}")
                st.markdown("### 🏩 Sector Regulators")
                for reg in details.get("regulators", []):
                    st.markdown(f"- {reg}")
                st.markdown("### 📊 ISO 27001 Readiness")
                if details["iso27001_expected"]:
                    st.markdown("✅ Likely to be ISO 27001 compliant or in-progress")
                else:
                    st.markdown("⚠️ May lack ISO 27001; consider IT maturity uplift advisory")

                # ISO 27001 AI Check
                st.markdown("### 🧐 ISO 27001 Public Evidence Check (via AI)")
                st.info("Asking Cohere AI: *Does this organization have ISO 27001 certification based on public data?*")

                iso_check_prompt = f"""
Check if the organization named \"{company_input}\" is ISO/IEC 27001 certified.

Only use publicly known information, such as:
- Official announcements
- Company press releases
- References on their website
- Known certifications by registrars

If there's no information, say so clearly.
Respond in a short, objective, non-assumptive paragraph.
"""

                try:
                    iso_response = co.chat(
                        model="command-r-plus",
                        message=iso_check_prompt,
                        temperature=0.3
                    )
                    iso_text = iso_response.text.strip()
                    st.markdown(f"> 📜 **Cohere says:** {iso_text}")
                    st.caption("💡 This is AI-generated text. Please verify or decide manually.")
                except Exception as e:
                    st.warning(f"❗ Could not fetch ISO 27001 info: {e}")

            else:
                st.warning("❗ Sector returned by AI is not mapped in your catalog.")

        except Exception as e:
            st.error(f"❌ Could not parse AI result: {e}")
    else:
        st.error(f"❌ Failed to get classification: {result[1]}")
