"""
Demo Script for AssuRisk Policy Generation System
=================================================
Demonstrates the key features and capabilities
"""

import os
from ai_policy_service import PolicyGenerationService
from policy_intents import (
    POLICY_CONTROL_MAP, 
    get_policy_intents, 
    validate_policy_coverage
)
from policy_template_structure import PolicyTemplateStructure


def print_header(title):
    """Prints a formatted section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70 + "\n")


def demo_list_policies():
    """Demo: List all available policies"""
    print_header("DEMO 1: Available Policies")
    
    print(f"Total policies available: {len(POLICY_CONTROL_MAP)}\n")
    
    # Show a sample
    sample_policies = list(POLICY_CONTROL_MAP.items())[:5]
    for policy_name, controls in sample_policies:
        print(f"📄 {policy_name}")
        print(f"   Controls: {', '.join(controls)}")
        intents = get_policy_intents(policy_name)
        if intents:
            print(f"   Intents defined: ✓ ({len(intents.get('mandatory_elements', []))} requirements)")
        else:
            print(f"   Intents defined: ✗")
        print()
    
    print(f"...and {len(POLICY_CONTROL_MAP) - 5} more policies")


def demo_policy_intents():
    """Demo: Show what intents look like"""
    print_header("DEMO 2: Policy Intents (Requirements)")
    
    policy_name = "Access Control Policy"
    intents = get_policy_intents(policy_name)
    
    print(f"Policy: {policy_name}\n")
    print(f"Description: {intents['description']}\n")
    print(f"Mandatory Elements ({len(intents['mandatory_elements'])}):")
    
    for i, element in enumerate(intents['mandatory_elements'][:5], 1):
        print(f"  {i}. {element}")
    
    if len(intents['mandatory_elements']) > 5:
        print(f"  ...and {len(intents['mandatory_elements']) - 5} more requirements\n")
    
    print(f"Audit Evidence Needed:")
    for evidence in intents.get('audit_evidence_needed', [])[:3]:
        print(f"  • {evidence}")


def demo_template_structure():
    """Demo: Show the 10-section template"""
    print_header("DEMO 3: Policy Template Structure")
    
    print("Every policy follows this 10-section audit-ready format:\n")
    
    for section_key, section_def in PolicyTemplateStructure.SECTIONS.items():
        print(f"{section_def['title']}")
        print(f"  → {section_def['description']}")
        print(f"  → Required elements: {len(section_def['required_elements'])}")
        print()


def demo_generate_policy(api_key=None):
    """Demo: Generate an actual policy (if API key is available)"""
    print_header("DEMO 4: Live Policy Generation")
    
    if not api_key:
        print("⚠️  Skipping - GEMINI_API_KEY not configured")
        print("To run this demo, set your API key:")
        print("  export GEMINI_API_KEY='your-key-here'")
        return
    
    print("Generating: ISMS Scope policy (this takes ~30-60 seconds)...\n")
    
    try:
        service = PolicyGenerationService(api_key=api_key)
        
        result = service.generate_policy(
            policy_name="ISMS Scope",
            company_name="AssuRisk Demo Corp"
        )
        
        if result["success"]:
            print("✓ Generation successful!\n")
            print("Metadata:")
            print(f"  Document ID: {result['metadata']['document_id']}")
            print(f"  Version: {result['metadata']['version']}")
            print(f"  Word count: {result['metadata']['word_count']}")
            print(f"  Mapped controls: {', '.join(result['metadata']['mapped_controls'])}")
            
            print("\nValidation:")
            val = result['validation']
            print(f"  Structure valid: {val['valid']}")
            print(f"  Sections found: {val['sections_found']}/{val['total_sections_required']}")
            print(f"  Mandatory statements: {val['mandatory_statements']}")
            
            print("\nIntent Coverage:")
            cov = result['intent_coverage']
            print(f"  Coverage: {cov['coverage_percentage']}%")
            print(f"  Audit ready: {cov['audit_ready']}")
            
            if cov.get('missing_elements'):
                print(f"\n  Missing elements:")
                for element in cov['missing_elements'][:3]:
                    print(f"    - {element}")
            
            # Show a snippet of the content
            print("\nGenerated Content (first 500 chars):")
            print("-" * 70)
            print(result['content'][:500] + "...")
            print("-" * 70)
            
            # Save to file
            output_file = "/home/claude/demo_generated_policy.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['content'])
            print(f"\n📄 Full policy saved to: {output_file}")
            
        else:
            print(f"✗ Generation failed: {result.get('error')}")
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def demo_validation():
    """Demo: Show how validation works"""
    print_header("DEMO 5: Policy Validation")
    
    # Create a sample (incomplete) policy
    sample_content = """# Access Control Policy

**Document ID:** POL-ACCESS-CONTROL-001
**Version:** 1.0.0
**Owner:** CISO

## 1. Purpose

This policy establishes access control requirements.

## 2. Scope

Applies to all systems.

## 5. Policy Statements

Users SHALL request access through proper channels.
"""
    
    print("Validating a sample policy with missing sections...\n")
    
    coverage = validate_policy_coverage("Access Control Policy", sample_content)
    
    print(f"Policy Name: {coverage['policy_name']}")
    print(f"Coverage: {coverage['coverage_percentage']}%")
    print(f"Audit Ready: {coverage['audit_ready']}")
    
    if coverage['missing_elements']:
        print(f"\nMissing Requirements ({len(coverage['missing_elements'])}):")
        for element in coverage['missing_elements'][:5]:
            print(f"  ✗ {element}")
        
        if len(coverage['missing_elements']) > 5:
            print(f"  ...and {len(coverage['missing_elements']) - 5} more")


def demo_statistics():
    """Demo: Show system statistics"""
    print_header("DEMO 6: System Statistics")
    
    total_policies = len(POLICY_CONTROL_MAP)
    policies_with_intents = len([p for p in POLICY_CONTROL_MAP.keys() if get_policy_intents(p)])
    
    # Count controls
    all_controls = set()
    for controls in POLICY_CONTROL_MAP.values():
        all_controls.update(controls)
    
    iso_controls = len([c for c in all_controls if c.startswith('ISO_') or c.startswith('A.')])
    soc_controls = len([c for c in all_controls if c.startswith('CC')])
    
    print(f"Total Policies: {total_policies}")
    print(f"Policies with Intents: {policies_with_intents} ({policies_with_intents/total_policies*100:.1f}%)")
    print(f"Unique Controls: {len(all_controls)}")
    print(f"  - ISO 27001: {iso_controls}")
    print(f"  - SOC 2: {soc_controls}")
    
    # Categorize by framework
    print("\nPolicies by Category:")
    categories = {
        "Context & Scope": 3,
        "Leadership": 3,
        "Planning": 4,
        "Support": 3,
        "Operational (A.5-A.8)": 50+,
        "Compliance": 5
    }
    
    for category, count in list(categories.items()):
        print(f"  {category}: {count} policies")


def main():
    """Run all demos"""
    print("\n" + "🎯 "*35)
    print(" "*20 + "AssuRisk Policy Generation System - DEMO")
    print("🎯 "*35)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Run demos
    demo_list_policies()
    input("\nPress Enter to continue to Demo 2...")
    
    demo_policy_intents()
    input("\nPress Enter to continue to Demo 3...")
    
    demo_template_structure()
    input("\nPress Enter to continue to Demo 4...")
    
    demo_generate_policy(api_key)
    input("\nPress Enter to continue to Demo 5...")
    
    demo_validation()
    input("\nPress Enter to continue to Demo 6...")
    
    demo_statistics()
    
    # Final message
    print_header("Demo Complete!")
    print("To generate policies for your organization:")
    print("\n1. Command Line:")
    print("   python batch_policy_generator.py --mode priority --company 'YourCo'")
    print("\n2. Python:")
    print("   from ai_policy_service import PolicyGenerationService")
    print("   service = PolicyGenerationService()")
    print("   result = service.generate_policy('Access Control Policy')")
    print("\n3. REST API:")
    print("   POST /api/policies/generate")
    print('   {"policy_name": "Access Control Policy", "company_name": "YourCo"}')
    print("\nSee README.md for full documentation.")
    print()


if __name__ == "__main__":
    main()
