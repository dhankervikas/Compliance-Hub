"""
Batch Policy Generation Script
==============================
Generates all 72 policies defined in POLICY_CONTROL_MAP with progress tracking,
validation, and database integration.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List
import time

from ai_policy_service import PolicyGenerationService
from policy_intents import POLICY_CONTROL_MAP


class BatchPolicyGenerator:
    """
    Orchestrates batch generation of all policies with progress tracking
    """
    
    def __init__(self, 
                 api_key: str = None,
                 company_name: str = "AssuRisk",
                 output_dir: str = "/home/claude/generated_policies"):
        """
        Initialize batch generator
        
        Args:
            api_key: Gemini API key
            company_name: Organization name
            output_dir: Directory to save generated policies
        """
        self.service = PolicyGenerationService(api_key)
        self.company_name = company_name
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/audit_ready", exist_ok=True)
        os.makedirs(f"{output_dir}/needs_review", exist_ok=True)
    
    def generate_all_policies(self, 
                            policy_filter: List[str] = None,
                            delay_seconds: int = 2) -> Dict:
        """
        Generates all policies or a filtered subset
        
        Args:
            policy_filter: Optional list of specific policy names to generate
            delay_seconds: Delay between API calls to avoid rate limiting
            
        Returns:
            Summary report dictionary
        """
        policies_to_generate = policy_filter if policy_filter else list(POLICY_CONTROL_MAP.keys())
        
        print(f"\n{'='*70}")
        print(f"BATCH POLICY GENERATION - {self.company_name}")
        print(f"{'='*70}")
        print(f"Total policies to generate: {len(policies_to_generate)}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*70}\n")
        
        results = {
            "start_time": datetime.now().isoformat(),
            "company_name": self.company_name,
            "total_policies": len(policies_to_generate),
            "successful": 0,
            "failed": 0,
            "audit_ready": 0,
            "needs_review": 0,
            "policies": {},
            "summary_by_category": {}
        }
        
        for i, policy_name in enumerate(policies_to_generate, 1):
            print(f"\n[{i}/{len(policies_to_generate)}] Generating: {policy_name}")
            print("-" * 70)
            
            try:
                # Generate the policy
                result = self.service.generate_policy(policy_name, self.company_name)
                
                if result.get("success"):
                    results["successful"] += 1
                    
                    # Check if audit ready
                    is_audit_ready = result["intent_coverage"]["audit_ready"] and result["validation"]["valid"]
                    
                    if is_audit_ready:
                        results["audit_ready"] += 1
                        subdirectory = "audit_ready"
                        status_icon = "✓"
                    else:
                        results["needs_review"] += 1
                        subdirectory = "needs_review"
                        status_icon = "⚠"
                    
                    # Save the policy
                    filename = f"{policy_name.replace(' ', '_').replace('/', '-')}.md"
                    filepath = os.path.join(self.output_dir, subdirectory, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(result["content"])
                    
                    # Print summary
                    print(f"{status_icon} Generated successfully")
                    print(f"  Word count: {result['metadata']['word_count']}")
                    print(f"  Intent coverage: {result['intent_coverage']['coverage_percentage']:.1f}%")
                    print(f"  Mandatory statements: {result['validation']['mandatory_statements']}")
                    print(f"  Status: {'AUDIT READY' if is_audit_ready else 'NEEDS REVIEW'}")
                    print(f"  Saved to: {filepath}")
                    
                    # Show any warnings
                    if result['validation']['warnings']:
                        print(f"  Warnings:")
                        for warning in result['validation']['warnings']:
                            print(f"    - {warning}")
                    
                    # Store result
                    results["policies"][policy_name] = {
                        "success": True,
                        "audit_ready": is_audit_ready,
                        "word_count": result['metadata']['word_count'],
                        "coverage": result['intent_coverage']['coverage_percentage'],
                        "filepath": filepath,
                        "controls": result['metadata']['mapped_controls']
                    }
                    
                else:
                    results["failed"] += 1
                    print(f"✗ Failed: {result.get('error')}")
                    
                    results["policies"][policy_name] = {
                        "success": False,
                        "error": result.get('error')
                    }
                
            except Exception as e:
                results["failed"] += 1
                print(f"✗ Exception: {str(e)}")
                
                results["policies"][policy_name] = {
                    "success": False,
                    "error": str(e)
                }
            
            # Rate limiting delay
            if i < len(policies_to_generate):
                time.sleep(delay_seconds)
        
        # Finalize results
        results["end_time"] = datetime.now().isoformat()
        results["duration_seconds"] = (
            datetime.fromisoformat(results["end_time"]) - 
            datetime.fromisoformat(results["start_time"])
        ).total_seconds()
        
        # Generate summary report
        self._generate_summary_report(results)
        
        # Print final summary
        self._print_final_summary(results)
        
        return results
    
    def generate_priority_policies(self) -> Dict:
        """
        Generates only the high-priority policies needed for Stage 1 audit
        
        Returns:
            Summary report
        """
        priority_policies = [
            # Mandatory ISO Clause 4-6 documents
            "ISMS Scope",
            "Context of the Organization",
            "Interested Parties",
            "Information Security Policy",
            "Risk Assessment Methodology",
            "Risk Treatment Plan",
            "Statement of Applicability (SoA)",
            
            # Critical operational policies
            "Access Control Policy",
            "Incident Response Policy",
            "Backup and Recovery Policy",
            "Data Classification Policy",
            "Acceptable Use Policy"
        ]
        
        print("\n🎯 PRIORITY POLICY GENERATION")
        print("Generating essential policies for Stage 1 audit readiness\n")
        
        return self.generate_all_policies(policy_filter=priority_policies)
    
    def _generate_summary_report(self, results: Dict):
        """Generates a detailed summary report"""
        report_path = os.path.join(self.output_dir, "generation_report.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 Full report saved to: {report_path}")
    
    def _print_final_summary(self, results: Dict):
        """Prints a final summary to console"""
        print("\n" + "="*70)
        print("GENERATION COMPLETE - SUMMARY")
        print("="*70)
        print(f"Total policies: {results['total_policies']}")
        print(f"✓ Successful: {results['successful']}")
        print(f"✗ Failed: {results['failed']}")
        print(f"✓ Audit ready: {results['audit_ready']}")
        print(f"⚠ Needs review: {results['needs_review']}")
        print(f"Duration: {results['duration_seconds']:.1f} seconds")
        print("="*70)
        
        if results['audit_ready'] > 0:
            print(f"\n✓ {results['audit_ready']} policies are audit-ready and saved to:")
            print(f"  {self.output_dir}/audit_ready/")
        
        if results['needs_review'] > 0:
            print(f"\n⚠ {results['needs_review']} policies need review and saved to:")
            print(f"  {self.output_dir}/needs_review/")
        
        if results['failed'] > 0:
            print(f"\n✗ {results['failed']} policies failed to generate:")
            for policy_name, policy_result in results['policies'].items():
                if not policy_result.get('success'):
                    print(f"  - {policy_name}: {policy_result.get('error', 'Unknown error')}")
    
    def generate_missing_policies(self, existing_policies: List[str]) -> Dict:
        """
        Generates only policies that don't already exist
        
        Args:
            existing_policies: List of policy names that already exist
            
        Returns:
            Summary report
        """
        all_policies = set(POLICY_CONTROL_MAP.keys())
        existing_set = set(existing_policies)
        missing_policies = list(all_policies - existing_set)
        
        if not missing_policies:
            print("✓ All policies already generated!")
            return {"message": "No missing policies"}
        
        print(f"\n📋 Found {len(missing_policies)} missing policies")
        return self.generate_all_policies(policy_filter=missing_policies)


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch generate compliance policies")
    parser.add_argument("--mode", choices=["all", "priority", "missing"], 
                       default="priority",
                       help="Generation mode: all (72 policies), priority (12 critical), missing (gaps)")
    parser.add_argument("--company", default="AssuRisk", 
                       help="Company name for policies")
    parser.add_argument("--output", default="/home/claude/generated_policies",
                       help="Output directory")
    parser.add_argument("--delay", type=int, default=2,
                       help="Delay in seconds between API calls")
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key before running:")
        print("  export GEMINI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Initialize generator
    generator = BatchPolicyGenerator(
        api_key=api_key,
        company_name=args.company,
        output_dir=args.output
    )
    
    # Run generation based on mode
    if args.mode == "all":
        results = generator.generate_all_policies(delay_seconds=args.delay)
    elif args.mode == "priority":
        results = generator.generate_priority_policies()
    elif args.mode == "missing":
        # For demo purposes, assume no existing policies
        results = generator.generate_missing_policies([])
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
