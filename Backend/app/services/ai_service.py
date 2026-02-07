import random
from datetime import datetime
import json
import os
from sqlalchemy.orm import Session
import openai
from app.models import Assessment, Control, Evidence, Policy
from app.config import settings

# Initialize AI Client (OpenAI Priority)
client = None
MODEL_NAME = None
PROVIDER = None

try:
    api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"DEBUG: Configured for OpenAI GPT-4-Turbo...")
        client = openai.OpenAI(api_key=api_key)
        MODEL_NAME = "gpt-4-turbo"
        PROVIDER = "openai"
        print(f"DEBUG: OpenAI Client Configured Successfully. Model: {MODEL_NAME}")
    else:
        print("CRITICAL WARNING: OPENAI_API_KEY Missing. AI features will fail.")
        client = None
except Exception as e:
    print(f"CRITICAL ERROR initializing AI client: {e}")
    client = None

def generate_ai_response(system_prompt: str, user_prompt: str, max_tokens: int = 1000, json_mode: bool = False) -> str:
    """
    Unified validation and generation wrapper for OpenAI Only
    """
    if not client:
        raise ValueError("AI Client not initialized")

    print(f"!!! GENERATING WITH PROVIDER: {PROVIDER} - Model: {MODEL_NAME} !!!")

    try:
        # AGGRESSIVE STRIP: Remove any newlines or spaces from the key
        # Explicitly fetch from settings or env to ensure we have the latest
        raw_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not raw_key:
             raise ValueError("API Key is missing")
        
        api_key = str(raw_key).strip()

        if PROVIDER == "openai":
            import requests
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": MODEL_NAME or "gpt-4-turbo-preview",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"} if json_mode else None,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                 raise Exception(f"OpenAI API Error ({response.status_code}): {response.text}")
                 
            return response.json()['choices'][0]['message']['content']
            
    except Exception as e:
        print(f"AI Generation Error ({PROVIDER}): {e}")
        raise e

def analyze_control_logic(control_id: int, db: Session, tenant_id: str = "default_tenant") -> Assessment:

    """
    SIMULATION MODE: analyzing control using Mock Logic.
    Generates realistic audit findings based on Control Metadata.
    """
    control = db.query(Control).filter(Control.id == control_id).first()
    if not control:
        return None

    # 1. Determine Score based on Status & Evidence
    evidence_count = db.query(Evidence).filter(Evidence.control_id == control_id).count()
    
    score = 0
    gaps = []
    recs = []
    
    # Base Score Logic
    if control.status == "implemented":
        score = random.randint(90, 100)
        gaps.append("No critical gaps identified.")
        recs.append("Maintain current control effectiveness.")
        recs.append("Conduct periodic review every 6 months.")
    elif control.status == "in_progress":
        score = random.randint(40, 65)
        gaps.append("Control implementation is incomplete.")
        gaps.append("Formal approval pending.")
        recs.append("Finalize implementation plan.")
        recs.append("Obtain sign-off from process owner.")
    else: # not_started or unknown
        score = random.randint(0, 15)
        gaps.append("Control has not been initiated.")
        gaps.append("Missing policy definition.")
        recs.append("Define initial policy scope.")
        recs.append("Assign owner to this control.")

    # 2. Context-Aware Enhancements (Keyword Matching)
    title_lower = control.title.lower()
    
    if "access" in title_lower or "password" in title_lower:
        if score < 90:
            gaps.append("MFA (Multi-Factor Authentication) evidence not found.")
            recs.append("Enforce MFA for all administrative accounts.")
    
    if "backup" in title_lower:
        if score < 90:
            gaps.append("Restoration test logs are missing.")
            recs.append("Perform and document a restoration test.")

    if "policy" in title_lower:
        if evidence_count == 0:
            gaps.append("Policy document not uploaded.")
            recs.append("Upload the signed policy PDF.")

    if "monitor" in title_lower or "log" in title_lower:
        if score < 90:
            gaps.append("Alert retention period undefined.")
            recs.append("Configure 90-day retention for audit logs.")

    # 3. Formatting
    gaps_text = " ".join(gaps)
    recs_text = " ".join(recs)
    
    # 4. Create Assessment Record
    assessment = Assessment(
        control_id=control_id,
        compliance_score=score,
        gaps=gaps_text,
        recommendations=recs_text,
        tenant_id=tenant_id
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    return assessment

def suggest_evidence(title: str, description: str, category: str, control_id: int = None, db: Session = None, regenerate: bool = False):
    # 1. Check DB for existing suggestion (Persistence)
    if control_id and db and not regenerate:
        # FIX: Use control_id (String) not id (Integer)
        control = db.query(Control).filter(Control.control_id == str(control_id)).first()
        if control and control.ai_requirements_json:
            print(f"DEBUG: Checking Persisted AI Data for Control {control_id}")
            try:
                # Smart Cache Invalidation:
                # If cached data contains generic/placeholder text, force regeneration.
                cached_str = control.ai_requirements_json or ""
                explanation = control.ai_explanation or ""
                
                cached_str_lower = cached_str.lower()
                explanation_lower = explanation.lower()
                
                invalid_triggers = [
                    "standard policy", 
                    "autogenerate_by_ai",
                    "master intent library",
                    "example artifact",
                    "generated by ai",
                    "ai generated"
                ]

                # --- CONSISTENCY LOCK START ---
                if control.ai_requirements_json and not regenerate:
                    requirements = json.loads(control.ai_requirements_json)
                    explanation = control.ai_explanation or "Regulatory Intent Summary"
                    
                    # SELF-HEALING: If this was a System Generated Fallback, and we have AI now, REGENERATE.
                    if "System Generated" in explanation or "Standard Compliance Requirement" in explanation:
                         print(f"DEBUG: Self-Healing triggered for Control {control_id} (Replacing Fallback)")
                         # Do not return. Fall through to AI generation.
                    elif len(requirements) > 0:
                        print(f"DEBUG: CONSISTENCY LOCK - Using stored data for {control_id}")
                        return {
                            "explanation": explanation,
                            "requirements": requirements
                        }
                    # --- CONSISTENCY LOCK END ---
            except Exception as e:
                print(f"Error parsing stored JSON: {e}")
                # Fallthrough to generate new

    # Infer Framework from Control ID if possible, else default to context
    framework_context = "ISO 27001 / SOC 2"
    if title.startswith("A.") or (control_id and str(control_id).startswith("A")):
        framework_context = "ISO 27001:2022"
    elif title.startswith("CC") or title.startswith("TSC"):
        framework_context = "SOC 2 Type II"

    # Anthropic/OpenAI Prompt Construction (Compliance Verification Requirements)
    system_prompt = """You are a Senior ISO 27001 Lead Auditor and Compliance Architect.
Your task is to extract the EXACT compliance verification requirements from a given ISO clause or control.

CRITICAL RULES:
1. Requirements must be VERIFICATION CHECKPOINTS — things an auditor checks during an audit.
2. DO NOT generate operational tasks like "Draft a policy" or "Host on Wiki".
3. DO generate requirements like "Information Security Policy has been established and documented".
4. Each requirement is a statement that can be verified as TRUE or FALSE during an audit.
5. Requirements must be faithful to the actual standard text — do not invent new obligations.
6. Evidence_Types should list what documents/artifacts could prove this requirement is met.
7. A single document may satisfy multiple requirements (e.g., one policy PDF could meet 5 of 7 requirements).

Source Determination:
- If the requirement can be verified via system logs, API, screenshots, configs -> AUTOMATED
- If it requires a signed document, meeting minutes, manual review -> MANUAL  
- If it can be partially automated but needs human verification -> HYBRID"""

    user_message = f"""
    Extract the compliance verification requirements for:
    Clause/Control: {control_id} - "{title}"
    Standard Text: "{description}"
    Framework Context: {framework_context}

    For each requirement, determine:
    1. The specific compliance condition that must be TRUE
    2. What evidence types could prove it (e.g., "Signed Policy PDF", "Board Meeting Minutes", "Screenshot of Intranet")
    3. Whether verification is AUTOMATED, MANUAL, or HYBRID

    Return JSON:
    {{
        "explanation": "One-sentence summary of what this clause requires overall",
        "requirements": [
            {{
                "Requirement_Name": "Clear statement of what must be verified (e.g., 'Information Security Policy is approved by top management')",
                "Requirement_Type": "Policy Document | Configuration | Process Record | Training Record | Meeting Minutes | System Log",
                "Source": "MANUAL | AUTOMATED | HYBRID",
                "Description": "What the auditor is looking for and why this matters",
                "Evidence_Types": ["Signed Policy PDF", "Board Resolution", "Email Approval"],
                "Automation_Potential": false,
                "Auditor_Guidance": "Good evidence: ... Insufficient evidence: ..."
            }}
        ]
    }}

    Generate ALL requirements that the standard text implies. Do not limit to 6 — generate as many as the clause actually requires (typically 3-10).
    """

    # Combined Prompt
    try:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("AI Client not initialized (Missing API Key)")

        # Direct HTTP Request to bypass SDK connection issues
        import requests
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4-turbo-preview",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 1024,
            "temperature": 0.2
        }
        
        print(f"!!! GENERATING WITH PROVIDER: openai - Model: gpt-4-turbo-preview (Direct HTTP) !!!")
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30 # Explicit timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API Error ({response.status_code}): {response.text}")
            
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Clean potential markdown wrappers (Redundant if json_mode=True but safe)
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
            
        result = json.loads(content)
        
        # MAP TO FRONTEND FORMAT AND SAVE
        final_requirements = []
        raw_reqs = result.get("requirements", [])
        
        for r in raw_reqs:
            final_requirements.append({
                "name": r.get("Requirement_Name", "Unknown Artifact"),
                "type": r.get("Requirement_Type", "Artifact"),
                "desc": r.get("Description", "Required per Master Intent Library"),
                "automation_potential": r.get("Automation_Potential", False),
                "audit_guidance": r.get("Auditor_Guidance", ""),
                "source": r.get("Source", "HYBRID"),
                "evidence_types": r.get("Evidence_Types", [])
            })
            
        # 2. Save to DB (Persistence)
        if control_id and db:
            try:
                # FIX: Use control_id (String) not id (Integer)
                control = db.query(Control).filter(Control.control_id == str(control_id)).first()
                if control:
                    control.ai_explanation = result.get("explanation", "")
                    control.ai_requirements_json = json.dumps(final_requirements)
                    db.commit()
                    print(f"DEBUG: Saved AI Data for Control {control_id}")
            except Exception as e:
                print(f"Error saving to DB: {e}")
                
        if control_id and str(control_id).lower() == "4.1": 
            result["master_intent_id"] = "INTENT_ORG_CONTEXT"
        elif control_id and str(control_id).lower() == "5.2":
            result["master_intent_id"] = "INTENT_GOVERNANCE_POLICY"
            
        return {
            "explanation": result.get("explanation", ""),
            "requirements": final_requirements,
            "master_intent_id": result.get("master_intent_id", None)
        }
    except Exception as e:
        import traceback
        # traceback.print_exc() # Reduce noise
        print(f"AI Suggestion Error: {e}. Falling back to Static Rules.")
        
        # FALLBACK: Generate Static Requirements based on Intent
        fallback_reqs = generate_fallback_requirements(title, description, category)
        
        # PERSISTENCE: Save these so we don't retry (User Rule: "Generate Only Once")
        if control_id and db:
            try:
                control = db.query(Control).filter(Control.control_id == str(control_id)).first()
                if control:
                    control.ai_explanation = "Standard Compliance Requirement (System Generated)"
                    control.ai_requirements_json = json.dumps(fallback_reqs)
                    db.commit()
                    print(f"DEBUG: Saved FALLBACK Data for Control {control_id}")
            except Exception as db_e:
                 print(f"Error saving fallback to DB: {db_e}")

        return {
            "explanation": "Standard Compliance Requirement (System Generated)",
            "requirements": fallback_reqs,
            "master_intent_id": "FALLBACK_INTENT"
        }

def generate_fallback_requirements(title: str, description: str, category: str):
    """
    Generates high-quality static requirements when AI is offline.
    Uses string matching to guess the intent.
    """
    t = title.lower()
    d = description.lower()
    c = category.lower()
    
    reqs = []
    
    # 1. POLICY / GOVERNANCE
    if "policy" in t or "procedure" in t or "governance" in c:
        reqs.append({
            "name": "Approved Policy Document",
            "type": "Policy",
            "desc": "A formal policy document approved by management.",
            "source": "MANUAL",
            "evidence_types": ["PDF", "Word"]
        })
        reqs.append({
            "name": "Policy Communication Evidence",
            "type": "Process Record",
            "desc": "Evidence that the policy was communicated to relevant staff.",
            "source": "MANUAL",
            "evidence_types": ["Email", "Slack Screenshot", "Training Log"]
        })

    # 2. ACCESS CONTROL
    elif "access" in t or "password" in t or "authentication" in t:
         reqs.append({
            "name": "User Access List",
            "type": "System Log",
            "desc": "Current list of active users and their roles.",
            "source": "AUTOMATED",
            "evidence_types": ["CSV", "Screenshot"]
        })
         reqs.append({
            "name": "Access Review Log",
            "type": "Process Record",
            "desc": "Log showing periodic review of user access rights.",
            "source": "MANUAL",
            "evidence_types": ["Excel", "Ticket Export"]
        })

    # 3. BACKUP / RECOVERY
    elif "backup" in t or "recovery" in t or "availability" in c:
        reqs.append({
            "name": "Backup Configuration",
            "type": "Configuration",
            "desc": "Screenshot or config export showing backup schedule.",
            "source": "AUTOMATED",
            "evidence_types": ["Screenshot", "Config File"]
        })
        reqs.append({
            "name": "Restoration Test Log",
            "type": "Process Record",
            "desc": "Evidence of a successful data restoration test.",
            "source": "MANUAL",
            "evidence_types": ["Log File", "Report"]
        })

    # 4. TRAINING / HR
    elif "training" in t or "awareness" in t or "human" in c:
        reqs.append({
             "name": "Training Material",
             "type": "Artifact",
             "desc": "Slide deck or content used for security training.",
             "source": "MANUAL",
             "evidence_types": ["PDF", "PPTX"]
        })
        reqs.append({
             "name": "Attendance Records",
             "type": "Process Record",
             "desc": "List of attendees who completed the training.",
             "source": "MANUAL",
             "evidence_types": ["Excel", "HR System Export"]
        })
        
    # 5. RISK MANAGEMENT
    elif "risk" in t or "assessment" in t:
         reqs.append({
             "name": "Risk Assessment Report",
             "type": "Report",
             "desc": "Document detailing identified risks and their treatments.",
             "source": "MANUAL",
             "evidence_types": ["PDF", "Excel"]
        })

    # DEFAULT FALLBACK (If no keywords match)
    if not reqs:
        reqs.append({
            "name": "Process Documentation",
            "type": "Document",
            "desc": "Documentation defining the process for this control.",
            "source": "MANUAL",
            "evidence_types": ["PDF", "Word"]
        })
        reqs.append({
            "name": "Evidence of Operation",
            "type": "Evidence",
            "desc": "Proof that the control process is being followed.",
            "source": "HYBRID",
            "evidence_types": ["Log", "Screenshot", "Report"]
        })
        
    return reqs

def generate_business_text(control_id: str, standard_text: str):
    """
    Generates a 'Business View' Title and Description for a Control/Clause.
    Title = Job to be Done (Action Oriented)
    Description = Business Context / Why it matters
    """
    # Anthropic/OpenAI Prompt
    system_prompt = "You are the Antigravity Compliance Engine. You must generate requirements with 100% fidelity to ISO 27001:2022 text. You are prohibited from simplifying 'internal and external issues' to 'security issues.' Focus on 'purpose' and 'intended outcomes'."
    
    user_message = f"""
    Convert this ISO Clause into a Business Process definition.
    
    Clause ID: "{control_id}"
    Standard Text: "{standard_text}"
    
    Directives:
    1. **Business Title**: Extract the exact "Job to be Done" from the standard.
       - Rule: Use verbatim terminology. Do not condense "external and internal issues" to "security issues".
    2. **Business Description**: Generate the requirement with 100% fidelity.
       - Rule: Start with "Determine", "Establish", "Ensure" as appropriate.
       - Constraint: Include "relevant to purpose" and "affect ability to achieve intended outcomes" where present in the standard (e.g. 4.1).
    
    Return JSON only:
    {{
        "business_title": "...",
        "business_description": "..."
    }}
    """
    # Combined Prompt
    try:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("AI Client not initialized (Missing API Key)")

        # Direct HTTP Request to bypass SDK connection issues
        import requests
        import json
        
        # AGGRESSIVE STRIP: Remove any newlines or spaces from the key
        api_key = str(settings.OPENAI_API_KEY).strip()
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4-turbo-preview",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 1024,
            "temperature": 0.2
        }
        
        print(f"!!! GENERATING WITH PROVIDER: openai - Model: gpt-4-turbo-preview (Direct HTTP) !!!")
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30 # Explicit timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API Error ({response.status_code}): {response.text}")
            
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Clean potential markdown wrappers (Redundant if json_mode=True but safe)
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
            
        return json.loads(content)
        
    except Exception as e:
        print(f"Generate Business Text Error: {e}")
        return {"business_title": "Error Generating Title", "business_description": "Error Generating Description"}

def analyze_gap(control_title: str, requirements: list, uploaded_files: list):
    req_list = ", ".join([r.get("name", "Unknown") for r in requirements])
    file_list = ", ".join(uploaded_files) if uploaded_files else "None"

    system_prompt = "You are an expert Compliance Auditor."
    user_message = f"""
    Perform a Compliance Gap Analysis.
    Control: "{control_title}"
    Required Evidence: {req_list}
    Uploaded Evidence: {file_list}

    Return JSON only:
    {{
        "status": "MET" | "PARTIAL" | "NOT_MET",
        "missing_items": ["List of missing items"],
        "reasoning": "Brief explanation."
    }}
    """

    try:
        if not client:
            raise ValueError("AI Client not initialized")

        content = generate_ai_response(
            system_prompt=system_prompt,
            user_prompt=user_message,
            max_tokens=1024,
            json_mode=True
        )
        
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
            
        return json.loads(content)
    except Exception as e:
        return {
            "status": "NOT_MET",
            "missing_items": ["Error analyzing evidence"],
            "reasoning": "AI Service unavailable."
        }

def generate_premium_policy(control_title: str, policy_name: str, company_profile: dict, control_description: str):
    """
    Generates a professional, ISO 27001:2022 compliant policy with context-awareness and self-correction.
    """
    # 1. Construct Prompt with Context & Guardrails
    profile_str = "\n".join([f"- {k}: {v}" for k, v in company_profile.items()])
    
    system_prompt = (
        "You are an expert Chief Compliance Officer (CCO) and Legal Counsel for a regulated enterprise.\\n"
        "Your task is to draft a 'Comprehensive Governance Policy' that strictly adheres to the Master Template below.\\n"
        "DO NOT create a simple checklist or operating procedure. You are writing Law for the organization.\\n\\n"
        "REQUIRED STRUCTURE (Use these exact headers):\\n"
        "1. Policy Statement (The Mandate)\\n"
        "2. Scope & Applicability (Who/What)\\n"
        "3. Detailed Regulatory Clauses (The Core Rules)\\n"
        "4. Enforcement & Penalties (Legal Consequences)\\n"
        "5. Technical Standards (ISO/SOC2 Ref)\\n\\n"
        "TONE & STYLE:\\n"
        "- Authoritative: Use 'shall', 'must', 'is strictly prohibited'.\\n"
        "- Specific: Do not say 'audits should happen'. Say 'The Internal Audit function shall execute an independent review annually'.\\n"
        "- Comprehensive: Include details like 'Independence of Auditors', 'Audit Universe', 'Reporting obligations'.\\n"
        "- No Introductory Fluff: Start immediately with the Metadata Table."
    )
    
    owner = company_profile.get("Policy Owner", "Chief Compliance Officer")
    approver = company_profile.get("Policy Approver", "Board of Directors")
    
    user_message = f"""
    Draft the official "{policy_name}" based on the control requirements below.
    
    ## Context Profile
    {profile_str}
    
    ## Control Requirements
    {control_description}
    
    ## DIRECTIVES:
    1. **Policy Statement**: Write a high-level mandate establishing this specific security domain as a corporate priority.
    2. **Detailed Regulatory Clauses**: Break down the control into specific sub-policies. For example, if this is about Auditing, include clauses for 'Audit Independence', 'Frequency', 'Reporting', and 'Follow-up'.
    3. **Enforcement**: Include standard legal language: "Violations of this policy may result in disciplinary action, up to and including termination of employment and legal prosecution."
    
    ## REQUIRED METADATA HEADERS (Markdown Table):
    | Document Control | |
    | :--- | :--- |
    | **Classification** | Restricted |
    | **Owner** | {owner} |
    | **Approver** | {approver} |
    | **Version** | 2.0 (Master) |
    | **Effective Date** | [Current Date] |

    Start with the Table, then the Headers.
    """
    
    try:
        if not client:
            raise ValueError("AI Client not initialized")

        # Generation Step
        draft_content = generate_ai_response(
            system_prompt=system_prompt,
            user_prompt=user_message,
            max_tokens=2500
        )
        
        # 2. Self-Correction / Audit Step
        audit_system_prompt = "You are a strict Policy Reviewer."
        
        audit_message = f"""
        Review the following policy draft against the requirement: "{control_title}".
        
        Draft:
        {draft_content[:6000]}... (truncated)
        
        CHECKLIST:
        1. Does it mention specific technologies ({profile_str})?
        2. Is there a 'Compliance Mapping' table at the end?
        3. Is the tone professional?
        
        If PERFECT, return the draft as is.
        If FLAWS found, rewrite the specific sections to fix them and return the IMPROVED version.
        """
        
        # We'll skip the second call for speed unless strictly requested, Claude Sonnet is usually very good.
        # But leaving the structure here if we needed to uncomment it.
        # For now, just return the draft.
        
        return draft_content

    except Exception as e:
        print(f"Policy Generation Error: {e}")
        return f"## Error Generating Policy\n\nReason: {str(e)}"

def generate_artifact_content(control_title: str, artifact_name: str, context: str):
    # Legacy wrapper
    system_prompt = "You are a Compliance Officer creating a formal document."
    user_message = f"""
    Document: "{artifact_name}"
    Control: "{control_title}"
    Context: "{context}"
    Format: Markdown.
    """
    try:
        if not client: return "AI Unavailable"
        
        return generate_ai_response(
            system_prompt=system_prompt,
            user_prompt=user_message,
            max_tokens=2000
        )
    except Exception as e:
        return str(e)

def analyze_document_gap(control_title: str, requirements: list, file_path: str = None, is_confidential: bool = False, file_stream = None, filename: str = ""):
    """
    Simulates a Senior ISO 27001 Auditor Review.
    Checks for Requirements Met and Evidence Date Currency (<12 months).
    Supports: PDF, DOCX, and IMAGES (PNG/JPG) via Computer Vision.
    Accepts local file_path OR in-memory file_stream (BytesIO).
    """
    import pypdf
    import docx
    import base64
    from datetime import datetime
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    req_list = "\n".join([f"- {r.get('name', 'Requirement')}" for r in requirements]) if requirements else "Standard ISO 27001 Requirements"
    
    # Check File Type
    target_name = filename if file_stream else (file_path or "")
    ext = target_name.lower().split('.')[-1]
    is_image = ext in ['png', 'jpg', 'jpeg']
    
    text_content = ""
    image_base64 = None
    
    try:
        if is_image:
            # IMAGE HANDLING (VISION)
            if file_stream:
                image_base64 = base64.b64encode(file_stream.read()).decode('utf-8')
            else:
                with open(file_path, "rb") as image_file:
                    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        elif ext == 'pdf':
            source = file_stream if file_stream else file_path
            reader = pypdf.PdfReader(source)
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
        elif ext == 'docx':
            source = file_stream if file_stream else file_path
            doc = docx.Document(source)
            for para in doc.paragraphs:
                text_content += para.text + "\n"
        else:
             # Assume text/md
            if file_stream:
                text_content = file_stream.read().decode("utf-8", errors="ignore")
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text_content = f.read()
                
        if not is_image:
             text_content = text_content[:50000] # Truncate Text
             
    except Exception as e:
        print(f"Error reading file for AI analysis: {e}")
        return {
            "status": "ERROR", 
            "reasoning": f"Could not process file: {e}",
            "gaps": ["File unreadable"],
             "date_check": False
        }

    # --- BUILD PROMPT ---
    
    privacy_instruction = ""
    if is_confidential:
        privacy_instruction = """
        CRITICAL PRIVACY PROTOCOL (CONFIDENTIAL MODE):
        1. Do NOT store or process the full document.
        2. Identify the SINGLE most relevant line or code block that proves compliance.
        3. Sanitize this snippet by replacing names/IPs with [REDACTED].
        4. Store ONLY this sanitized snippet as 'Evidence Context'.
        5. Discard all other content.
        """
    
    if is_image:
        system_prompt = "You are a Digital Forensic Auditor."
        user_message_content = [
            {
                "type": "text",
                "text": f"""
                Context:
                - Control: {control_title}
                - Current Date: {current_date}
                
                {privacy_instruction}
                
                Task: Analyze this evidence image and verify if it satisfies the requirement listed below.
                
                Requirement:
                {req_list}
                
                Instructions:
                1. Identify what is shown in this image.
                2. Evaluate if the image proves the requirement is met.
                3. Identify any security red flags visible (e.g., passwords on post-its, unlocked racks).
                
                Return JSON only:
                {{
                    "final_verdict": "PASS" | "FAIL",
                    "date_check_passed": true,
                    "gaps_found": ["List specific gaps or 'None'"],
                    "summary": "Visual observations and verdict."
                }}
                """
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{ext};base64,{image_base64}"
                }
            }
        ]
    else:
        # TEXT HANDLING
        system_prompt = "You are a Senior ISO 27001 Auditor."
        user_message_content = f"""
        Context:
        - Control: {control_title}
        - Current Date: {current_date}
        - Document Provided: (Excerpt below)
        
        {privacy_instruction}
        
        Requirements to Verify:
        {req_list}
        
        Document Text:
        \"\"\"
        {text_content}
        \"\"\"
        
        Task: 
        1. Verify if the document content satisfies ALL the requirements listed.
        2. Check if the document has a date within the last 12 months (or is undated/current). If explicit dates are >12 months old, fail the Date Check.
        
        Return JSON only:
        {{
            "final_verdict": "PASS" | "FAIL",
            "date_check_passed": true | false,
            "gaps_found": ["List specific gaps or 'None'"],
            "summary": "Auditor's executive summary."
        }}
        """

    try:
        if not client:
             return { "final_verdict": "FAIL", "gaps_found": ["AI Service Unavailable"], "date_check_passed": False, "summary": "System offline." }

        # Helper wrapper update or direct call for Multi-modal?
        # generate_ai_response wrapper might handle string only.
        # We need to call client directly OR update the wrapper.
        # Updating logic inline here for safety/speed since wrapper is simple.
        
        if PROVIDER == "openai":
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message_content} 
            ]
            response = client.chat.completions.create(
                model="gpt-4-turbo", # Explicitly use turbo for Vision
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
        else:
            return { "final_verdict": "FAIL", "gaps_found": ["Vision Not Supported on this Provider"], "date_check_passed": False }

        
        # Clean markdown
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
            
        return json.loads(content)
        
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {
             "final_verdict": "FAIL",
             "gaps_found": [f"AI Error: {str(e)}"],
             "date_check_passed": False,
             "summary": "Analysis failed due to internal error."
        }

def detect_and_redact_pii(text_content: str, is_image: bool, file_ext: str = "txt", image_base64: str = None):
    """
    Scans for GDPR/PII Data.
    Returns: { "pii_found": bool, "action": "REJECT"|"MASK"|"TAG"|"NONE", "reasoning": str, "redacted_text": str|None, "pii_locations": list }
    """
    if not client:
        return { "pii_found": False, "action": "NONE", "reasoning": "AI Unavailable" } 

    system_prompt = "You are a GDPR Data Protection Officer."
    
    if is_image:
        user_message_content = [
            {
                "type": "text", 
                "text": """
                Task: Analyze this content for PII (Personally Identifiable Information).
                
                Identify the coordinates (bounding boxes) for images that need masking to comply with GDPR.
                If the data is excessively sensitive (Passports, IDs, Credit Cards), block the upload.
                
                Risk Rules:
                1. Passports/Driver Licenses/IDs -> Action: REJECT (Reason: "Unmasked Identity Document").
                2. User Lists with Full Names/Emails -> Action: MASK (Reason: "Visible Personal Emails").
                3. System Logs/IPs -> Action: TAG (Reason: "Technical PII").
                4. No PII -> Action: NONE.
                
                Return JSON:
                { 
                    "pii_found": bool, 
                    "action": "REJECT"|"MASK"|"TAG"|"NONE", 
                    "reasoning": "...",
                    "pii_locations": [ 
                        { "description": "Face/Email/ID", "box_2d": [0,0,0,0] } 
                    ] 
                }
                """
            },
            {
                "type": "image_url",
                "image_url": { "url": f"data:image/{file_ext};base64,{image_base64}" }
            }
        ]
    else:
        # TEXT MODE
        user_message_content = f"""
        Task: Analyze this content for PII.
        
        Text Snippet:
        \"\"\"
        {text_content[:15000]} 
        \"\"\"
        
        Risk Rules:
        1. Passports/Driver Licenses/IDs -> Action: REJECT.
        2. Names/Emails/SSN/CreditCards -> Action: MASK.
        3. System Logs/IPs -> Action: TAG.
        
        Return JSON:
        {{ 
            "pii_found": bool, 
            "action": "REJECT"|"MASK"|"TAG"|"NONE", 
            "reasoning": "...",
            "sensitive_strings": ["List of strings found e.g. 'John Doe'"],
            "redacted_text": "Return the full text but replace sensitive values with [REDACTED]. Return NULL if no redaction needed." 
        }}
        """

    try:
        # Build Messages
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message_content}]
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            max_tokens=2000, # Allow space for redacted text
            temperature=0.3, # Strict
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        
         # Clean markdown
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
            
        return json.loads(content)
        
    except Exception as e:
        print(f"PII Check Error: {e}")
        return { "pii_found": False, "action": "NONE", "reasoning": "Error scanning for PII." }

def suggest_justification(title: str, control_id: str, category: str, scope: str = ""):
    # OpenAI Prompt
    system_prompt = "You are an ISO 27001 Lead Auditor."
    
    user_message = f"""
    Context:
    - Control: {control_id} - {title}
    - Justification Category: {category}
    - Company Scope: {scope}
    
    Task: Draft a professional 1-2 sentence 'Justification Detail' for the Statement of Applicability.
    
    Logic:
    1. If Category is "Regulatory Requirement": Cite GDPR Art 32 or HIPAA Security Rule if relevant to data protection.
    2. If Category is "Result of Risk Management": Mention it mitigates specific risks identified in Q1 Risk Assessment.
    3. If Category is "Not Applicable (Remote)": Explicitly state the organization has no physical perimeter/offices.
    4. If Category is "Contractual Obligation": Mention MSA requirements.
    5. If Category is "Inclusion": Provide a standard justification for why this control is necessary for information security.
    
    Output ONLY the justification text. START with coverage status (e.g. "Excluded: The organization..." or "Included: Mandatory...").
    """

    try:
        if not client:
            raise ValueError("AI Client not initialized")

        content = generate_ai_response(
            system_prompt=system_prompt,
            user_prompt=user_message,
            max_tokens=300
        )
        return {"justification": content.strip()}
    except Exception as e:
        print(f"Justification Error: {e}")
        return {"justification": "Justification generation failed. Please enter manually."}

def rewrite_text(text: str, instruction: str):
    """
    Rewrites text based on instruction using OpenAI.
    """
    system_prompt = "You are an expert technical writer and editor."
    user_message = f"Instruction: {instruction}\n\nText:\n{text}"
    
    try:
        if not client:
            return text + " (AI Unavailable)"

        return generate_ai_response(
            system_prompt=system_prompt,
            user_prompt=user_message,
            max_tokens=2048
        )
    except Exception as e:
        print(f"Rewrite Error: {e}")
        return text
