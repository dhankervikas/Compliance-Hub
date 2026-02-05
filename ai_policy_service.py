"""
AI Policy Generation Service
============================
Generates audit-ready policy content using Google Gemini with strict intent adherence
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import google.generativeai as genai

from policy_template_structure import PolicyTemplateStructure
from policy_intents import get_policy_intents, get_mapped_controls, POLICY_CONTROL_MAP


class PolicyGenerationService:
    """
    Service for generating ISO 27001:2022 and SOC 2 compliant policies using AI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the service with Gemini API
        
        Args:
            api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-001')
        self.template_structure = PolicyTemplateStructure()
    
    def _build_generation_prompt(self, policy_name: str, company_name: str = "AssuRisk") -> str:
        """
        Constructs the detailed prompt for policy generation
        
        Args:
            policy_name: Name of the policy to generate
            company_name: Name of the organization
            
        Returns:
            Formatted prompt string
        """
        intents = get_policy_intents(policy_name)
        controls = get_mapped_controls(policy_name)
        
        if not intents:
            raise ValueError(f"No intents defined for policy: {policy_name}")
        
        prompt = f"""You are an expert information security auditor and policy writer specializing in ISO 27001:2022 and SOC 2 compliance.

TASK: Generate a comprehensive, audit-ready policy for "{policy_name}" for {company_name}.

CRITICAL REQUIREMENTS - MUST BE FOLLOWED EXACTLY:

1. STRUCTURE: Use the 10-section format below with these EXACT headers:
   - 1. Purpose
   - 2. Scope
   - 3. Definitions
   - 4. Roles and Responsibilities
   - 5. Policy Statements
   - 6. Procedures and Implementation
   - 7. Exceptions and Deviations
   - 8. Compliance and Monitoring
   - 9. Enforcement and Violations
   - 10. Policy Review and Maintenance

2. MANDATORY COMPLIANCE ELEMENTS (YOU MUST INCLUDE ALL OF THESE):
"""
        
        # Add mandatory elements
        for i, element in enumerate(intents.get("mandatory_elements", []), 1):
            prompt += f"   {i}. {element}\n"
        
        prompt += f"\n3. MAPPED CONTROLS (Reference these explicitly):\n"
        for control in controls:
            prompt += f"   - {control}\n"
        
        # Add section-specific requirements
        if "section_specific_requirements" in intents:
            prompt += "\n4. SECTION-SPECIFIC REQUIREMENTS:\n"
            for section, requirements in intents["section_specific_requirements"].items():
                prompt += f"\n   {section.upper()}:\n"
                if isinstance(requirements, list):
                    for req in requirements:
                        prompt += f"   - {req}\n"
                else:
                    prompt += f"   - {requirements}\n"
        
        prompt += f"""

5. QUALITY STANDARDS:
   - Minimum 1500 words total
   - Use "SHALL" and "MUST" for mandatory requirements (minimum 5 instances)
   - Use "SHOULD" for recommended practices
   - Include specific, measurable criteria where possible
   - Write in professional, auditor-approved language
   - Avoid vague statements like "appropriate" without defining criteria
   - Include concrete examples where helpful

6. TONE AND STYLE:
   - Professional and authoritative
   - Clear and unambiguous
   - Action-oriented (use active voice)
   - Suitable for external audit presentation
   - Consistent terminology throughout

7. METADATA TO INCLUDE AT TOP:
   **Document ID:** POL-{policy_name.replace(' ', '-').upper()}-001
   **Version:** 1.0.0
   **Effective Date:** {datetime.now().strftime('%Y-%m-%d')}
   **Next Review:** {(datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')}
   **Owner:** Chief Information Security Officer (CISO)
   **Classification:** Internal

IMPORTANT VALIDATION CHECKS YOUR OUTPUT MUST PASS:
- All 10 sections are present with substantial content
- All mandatory elements from the list above are addressed
- All mapped controls are explicitly referenced
- Policy contains measurable compliance criteria
- Language is precise and enforceable

Now generate the complete policy content in Markdown format:"""
        
        return prompt
    
    def generate_policy(self, 
                       policy_name: str, 
                       company_name: str = "AssuRisk",
                       temperature: float = 0.3) -> Dict:
        """
        Generates a complete policy document
        
        Args:
            policy_name: Name of the policy (must be in POLICY_CONTROL_MAP)
            company_name: Organization name
            temperature: AI creativity level (lower = more deterministic)
            
        Returns:
            Dictionary containing:
                - content: Generated Markdown policy
                - metadata: Policy metadata
                - validation: Validation results
                - intents_coverage: How well intents were covered
        """
        if policy_name not in POLICY_CONTROL_MAP:
            raise ValueError(f"Unknown policy: {policy_name}. Must be one of {list(POLICY_CONTROL_MAP.keys())}")
        
        # Build the prompt
        prompt = self._build_generation_prompt(policy_name, company_name)
        
        # Generate content
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': temperature,
                    'max_output_tokens': 8192,
                }
            )
            
            generated_content = response.text
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Generation failed: {str(e)}",
                "policy_name": policy_name
            }
        
        # Validate the generated content
        validation_results = self._validate_generated_policy(policy_name, generated_content)
        
        # Calculate intent coverage
        from policy_intents import validate_policy_coverage
        coverage = validate_policy_coverage(policy_name, generated_content)
        
        return {
            "success": True,
            "policy_name": policy_name,
            "content": generated_content,
            "metadata": {
                "document_id": f"POL-{policy_name.replace(' ', '-').upper()}-001",
                "version": "1.0.0",
                "effective_date": datetime.now().strftime('%Y-%m-%d'),
                "next_review_date": (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
                "owner": "Chief Information Security Officer (CISO)",
                "classification": "Internal",
                "mapped_controls": get_mapped_controls(policy_name),
                "word_count": len(generated_content.split()),
                "generated_at": datetime.now().isoformat()
            },
            "validation": validation_results,
            "intent_coverage": coverage
        }
    
    def _validate_generated_policy(self, policy_name: str, content: str) -> Dict:
        """
        Validates generated policy against structure and quality requirements
        
        Args:
            policy_name: Name of the policy
            content: Generated policy content
            
        Returns:
            Validation results dictionary
        """
        errors = []
        warnings = []
        
        # Check for all 10 required sections
        required_sections = [
            "1. Purpose",
            "2. Scope",
            "3. Definitions",
            "4. Roles and Responsibilities",
            "5. Policy Statements",
            "6. Procedures and Implementation",
            "7. Exceptions and Deviations",
            "8. Compliance and Monitoring",
            "9. Enforcement and Violations",
            "10. Policy Review and Maintenance"
        ]
        
        for section in required_sections:
            if section not in content:
                errors.append(f"Missing required section: {section}")
        
        # Check word count
        word_count = len(content.split())
        if word_count < 1500:
            warnings.append(f"Policy is short ({word_count} words). Minimum 1500 recommended.")
        
        # Check for mandatory language
        shall_count = content.count("SHALL") + content.count("shall")
        must_count = content.count("MUST") + content.count("must")
        
        if (shall_count + must_count) < 5:
            warnings.append(f"Insufficient mandatory language. Found {shall_count + must_count} SHALL/MUST statements, minimum 5 recommended.")
        
        # Check for control references
        controls = get_mapped_controls(policy_name)
        missing_controls = []
        for control in controls:
            if control not in content:
                missing_controls.append(control)
        
        if missing_controls:
            warnings.append(f"Some mapped controls not explicitly referenced: {', '.join(missing_controls[:3])}")
        
        # Check for metadata
        required_metadata = ["Document ID:", "Version:", "Effective Date:", "Owner:"]
        for meta in required_metadata:
            if meta not in content:
                errors.append(f"Missing metadata: {meta}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "word_count": word_count,
            "mandatory_statements": shall_count + must_count,
            "sections_found": len([s for s in required_sections if s in content]),
            "total_sections_required": len(required_sections)
        }
    
    def batch_generate_policies(self, 
                                policy_names: List[str], 
                                company_name: str = "AssuRisk") -> Dict:
        """
        Generates multiple policies in batch
        
        Args:
            policy_names: List of policy names to generate
            company_name: Organization name
            
        Returns:
            Dictionary with results for each policy
        """
        results = {
            "total": len(policy_names),
            "successful": 0,
            "failed": 0,
            "policies": {}
        }
        
        for policy_name in policy_names:
            print(f"Generating: {policy_name}...")
            
            try:
                result = self.generate_policy(policy_name, company_name)
                
                if result.get("success"):
                    results["successful"] += 1
                    results["policies"][policy_name] = result
                    
                    # Print validation summary
                    if result["validation"]["valid"]:
                        print(f"  ✓ Generated successfully ({result['metadata']['word_count']} words)")
                    else:
                        print(f"  ⚠ Generated with errors:")
                        for error in result["validation"]["errors"]:
                            print(f"    - {error}")
                else:
                    results["failed"] += 1
                    results["policies"][policy_name] = result
                    print(f"  ✗ Failed: {result.get('error')}")
                    
            except Exception as e:
                results["failed"] += 1
                results["policies"][policy_name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"  ✗ Exception: {str(e)}")
        
        return results
    
    def regenerate_section(self, 
                          policy_name: str, 
                          section_name: str, 
                          current_content: str,
                          feedback: str = "") -> str:
        """
        Regenerates a specific section of a policy
        
        Args:
            policy_name: Name of the policy
            section_name: Section to regenerate (e.g., "5. Policy Statements")
            current_content: Current full policy content
            feedback: Optional feedback on what to improve
            
        Returns:
            Regenerated section content
        """
        intents = get_policy_intents(policy_name)
        section_requirements = intents.get("section_specific_requirements", {}).get(
            section_name.split('.')[1].strip().lower().replace(' ', '_'), 
            []
        )
        
        prompt = f"""You are regenerating section "{section_name}" for the "{policy_name}" policy.

CURRENT SECTION CONTENT:
{self._extract_section(current_content, section_name)}

REQUIREMENTS FOR THIS SECTION:
{section_requirements}

USER FEEDBACK:
{feedback if feedback else "Make this section more comprehensive and audit-ready."}

Generate an improved version of this section that:
1. Addresses all requirements listed above
2. Is more specific and measurable
3. Uses appropriate mandatory language (SHALL/MUST)
4. Maintains professional auditor-approved tone

Output only the section content (including the section header):"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error regenerating section: {str(e)}"
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extracts a specific section from policy content"""
        lines = content.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            if line.startswith(section_name):
                in_section = True
                section_lines.append(line)
            elif in_section:
                if line.startswith(('#', '##')) and any(str(i) in line for i in range(1, 11)):
                    # Hit the next section
                    break
                section_lines.append(line)
        
        return '\n'.join(section_lines)


# Convenience function for quick generation
def generate_policy_quick(policy_name: str, 
                         api_key: Optional[str] = None,
                         company_name: str = "AssuRisk") -> Dict:
    """
    Quick generation of a single policy
    
    Args:
        policy_name: Name of policy to generate
        api_key: Gemini API key (optional)
        company_name: Organization name
        
    Returns:
        Generation result dictionary
    """
    service = PolicyGenerationService(api_key)
    return service.generate_policy(policy_name, company_name)


if __name__ == "__main__":
    # Example usage
    print("AssuRisk Policy Generation Service")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ GEMINI_API_KEY not set in environment")
        print("Please set it before running policy generation")
        exit(1)
    
    service = PolicyGenerationService()
    
    # Example: Generate ISMS Scope
    print("\nGenerating 'ISMS Scope' policy...")
    result = service.generate_policy("ISMS Scope")
    
    if result["success"]:
        print(f"\n✓ Successfully generated!")
        print(f"  Word count: {result['metadata']['word_count']}")
        print(f"  Intent coverage: {result['intent_coverage']['coverage_percentage']}%")
        print(f"  Audit ready: {result['intent_coverage']['audit_ready']}")
        
        if result['validation']['warnings']:
            print(f"\n⚠ Warnings:")
            for warning in result['validation']['warnings']:
                print(f"  - {warning}")
        
        # Save to file
        output_file = f"/home/claude/generated_policy_{result['metadata']['document_id']}.md"
        with open(output_file, 'w') as f:
            f.write(result['content'])
        print(f"\n📄 Saved to: {output_file}")
    else:
        print(f"\n❌ Generation failed: {result.get('error')}")
