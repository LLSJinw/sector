import streamlit as st
import cohere

# Initialize Cohere Chat model with your API key
co = cohere.Client("sNIAP0wwbfOagyZr75up0a6tVejuZ6ONH0ODCsOa")

# Sector-to-service mapping
SECTOR_DETAILS = {
    "Critical Infrastructure (CII)": {
        "key_services": [
            "Cyber Risk Assessment (IT/OT)",
            "Tabletop Exercise (TTX)",
            "CIRP & Playbook"
        ],
        "secondary_opportunities": [
            "Gap Assessment",
            "BCP Alignment"
        ],
        "iso27001_expected": True
    },
    "Banking / Finance / Insurance (BFSI)": {
        "key_services": [
            "PDPA Consult",
            "Pentest",
            "IRP & Playbook"
        ],
        "secondary_opportunities": [
            "Source Code Scan",
            "Awareness Training"
        ],
        "iso27001_expected": True
    },
    "Healthcare": {
        "key_services": [
            "PDPA Consult",
            "IRP & TTX"
        ],
        "secondary_opportunities": [
            "Phishing Simulation",
            "Awareness Training"
        ],
        "iso27001_expected": False
    },
    "Government / SOE": {
        "key_services": [
            "TTX",
            "IRP",
            "Cyber Risk Assessment"
        ],
        "secondary_opportunities": [
            "Gap Assessment",
            "อว3/อช3 Consult"
        ],
        "iso27001_expected": False
    },
    "Telco / ISP": {
        "key_services": [
            "Zero Trust Readiness",
            "CIRP"
        ],
        "secondary_opportunities": [
            "Gap Assessment",
            "Managed CSOC"
        ],
        "iso27001_expected": True
    },
    "Software / Tech / SaaS": {
        "key_services": [
            "Secure SDLC Gap Assessment",
            "Source Code Scan",
            "Pentest"
        ],
        "secondary_opportunities": [
            "Awareness Training",
            "CI/CD Security"
        ],
        "iso27001_expected": True
    },
    "Retail / SME / Logistics": {
        "key_services": [
            "VA Scan",
            "PDPA Consult"
        ],
        "secondary_opportunities": [
            "Awareness Training",
            "Phishing Simulation"
        ],
        "iso27001_expected": False
    },
    "Manufacturing / OT-heavy": {
        "key_services": [
            "Cyber Risk Assessment (IT/OT)",
            "CIRP"
        ],
        "secondary_opportunities": [
            "TTX",
            "Backup/Restore Drill"
        ],
        "iso27001_expected": False
    }
}

# Chat prompt logic
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

        # Try to extract sector name
        import json
        try:
            parsed = json.loads(result)
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
                st.markdown("### 📊 ISO 27001 Readiness")
                if details["iso27001_expected"]:
                    st.markdown("✅ Likely to be ISO 27001 compliant or in-progress")
                else:
                    st.markdown("⚠️ May lack ISO 27001; consider IT maturity uplift advisory")
            else:
                st.warning("❗ Sector returned by AI is not mapped in your catalog.")
        except Exception as e:
            st.error(f"❌ Could not parse AI result: {e}")
    else:
        st.error(f"❌ Failed to get classification: {result[1]}")

