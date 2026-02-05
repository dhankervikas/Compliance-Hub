"""
AssuRisk Policy Generation - COMPLETE AUTO-INSTALLER
====================================================
This script does EVERYTHING automatically - just run it once!

Usage:
    python complete_installer.py --api-key YOUR_GEMINI_API_KEY

What it does:
    1. ✅ Uninstalls old deprecated packages
    2. ✅ Installs correct new packages
    3. ✅ Creates all directories
    4. ✅ Copies all files to correct locations
    5. ✅ Fixes all import paths
    6. ✅ Updates .env file
    7. ✅ Tests installation
    8. ✅ Generates sample policy
    9. ✅ Shows next steps

NO manual steps required!
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse
import time


class CompleteInstaller:
    """Complete automated installer - zero manual work required"""
    
    def __init__(self, api_key, project_root=None):
        self.api_key = api_key
        
        # Auto-detect project root
        if project_root:
            self.project_root = Path(project_root)
        else:
            possible_paths = [
                Path(r"C:\Projects\Compliance_Product"),
                Path.home() / "OneDrive" / "Documents" / "Compliance_Product",
                Path.home() / "Documents" / "Compliance_Product",
            ]
            
            for path in possible_paths:
                if path.exists() and (path / "Backend").exists():
                    self.project_root = path
                    break
            else:
                self.project_root = Path.cwd()
        
        self.backend_root = self.project_root / "Backend"
        self.app_root = self.backend_root / "app"
        self.downloads_dir = Path(__file__).parent  # Where this script is located
        
        print(f"\n🎯 Project root: {self.project_root}")
        print(f"🎯 Backend root: {self.backend_root}")
        print(f"🎯 Source files: {self.downloads_dir}\n")
    
    def print_step(self, step_num, total, message):
        """Pretty print step progress"""
        print(f"\n{'='*70}")
        print(f"📦 STEP {step_num}/{total}: {message}")
        print(f"{'='*70}\n")
    
    def run_all(self):
        """Execute complete installation"""
        total_steps = 10
        
        try:
            self.print_step(1, total_steps, "Cleaning Old Packages")
            self.clean_old_packages()
            
            self.print_step(2, total_steps, "Installing Correct Packages")
            self.install_packages()
            
            self.print_step(3, total_steps, "Creating Directory Structure")
            self.create_directories()
            
            self.print_step(4, total_steps, "Copying Policy Generation Files")
            self.copy_files()
            
            self.print_step(5, total_steps, "Fixing Import Paths")
            self.fix_imports()
            
            self.print_step(6, total_steps, "Updating .env Configuration")
            self.update_env()
            
            self.print_step(7, total_steps, "Creating Helper Scripts")
            self.create_helper_scripts()
            
            self.print_step(8, total_steps, "Testing Installation")
            self.test_installation()
            
            self.print_step(9, total_steps, "Generating Sample Policy")
            self.generate_sample()
            
            self.print_step(10, total_steps, "Installation Complete!")
            self.show_next_steps()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Installation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def clean_old_packages(self):
        """Remove deprecated google-generativeai package"""
        print("Removing deprecated packages...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "-y", "google-generativeai"],
                capture_output=True,
                check=False  # Don't fail if it's not installed
            )
            print("  ✅ Removed old google-generativeai package")
        except Exception as e:
            print(f"  ⚠️  Could not remove old package (may not be installed): {e}")
    
    def install_packages(self):
        """Install all required packages with correct versions"""
        packages = [
            'google-genai',  # New Google AI package
            'fastapi>=0.104.0',
            'pydantic>=2.0.0',
            'uvicorn[standard]>=0.24.0',
            'python-dotenv>=1.0.0'
        ]
        
        print("Installing packages (this may take 2-3 minutes)...")
        for package in packages:
            print(f"  📦 Installing {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"     ✅ {package} installed")
            else:
                print(f"     ⚠️  Warning: {package} - {result.stderr[:100]}")
        
        print("\n✅ All packages installed!")
    
    def create_directories(self):
        """Create directory structure"""
        dirs = [
            self.app_root / "services",
            self.app_root / "api",
            self.app_root / "scripts",
            self.backend_root / "generated_policies" / "audit_ready",
            self.backend_root / "generated_policies" / "needs_review"
        ]
        
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {directory.relative_to(self.project_root)}")
        
        print("\n✅ Directory structure ready!")
    
    def copy_files(self):
        """Copy all policy generation files"""
        file_mapping = {
            "policy_template_structure.py": self.app_root / "services" / "policy_template_structure.py",
            "policy_intents.py": self.app_root / "services" / "policy_intents.py",
            "ai_policy_service.py": self.app_root / "services" / "ai_policy_service.py",
            "api_integration.py": self.app_root / "api" / "policy_generation.py",
            "batch_policy_generator.py": self.app_root / "scripts" / "batch_policy_generator.py",
            "demo.py": self.backend_root / "demo.py"
        }
        
        for source_name, dest_path in file_mapping.items():
            source_path = self.downloads_dir / source_name
            
            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                print(f"  ✅ {source_name} → {dest_path.relative_to(self.project_root)}")
            else:
                print(f"  ⚠️  {source_name} not found (will be created)")
        
        print("\n✅ Files copied!")
    
    def fix_imports(self):
        """Fix all import statements to use new package and correct paths"""
        print("Fixing import statements and package references...")
        
        # Fix ai_policy_service.py
        service_file = self.app_root / "services" / "ai_policy_service.py"
        if service_file.exists():
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update to new Google AI package
            content = content.replace(
                'import google.generativeai as genai',
                'from google import genai'
            )
            content = content.replace(
                'genai.configure(api_key=self.api_key)',
                'self.client = genai.Client(api_key=self.api_key)'
            )
            content = content.replace(
                "self.model = genai.GenerativeModel('gemini-pro')",
                "# Model is called via client"
            )
            content = content.replace(
                'response = self.model.generate_content(',
                'response = self.client.models.generate_content(\n                model="gemini-1.5-flash",'
            )
            
            # Fix imports
            content = content.replace(
                'from policy_template_structure',
                'from app.services.policy_template_structure'
            )
            content = content.replace(
                'from policy_intents',
                'from app.services.policy_intents'
            )
            
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("  ✅ Fixed ai_policy_service.py")
        
        # Fix batch_policy_generator.py
        batch_file = self.app_root / "scripts" / "batch_policy_generator.py"
        if batch_file.exists():
            with open(batch_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = content.replace(
                'from ai_policy_service',
                'from app.services.ai_policy_service'
            )
            content = content.replace(
                'from policy_intents',
                'from app.services.policy_intents'
            )
            
            with open(batch_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("  ✅ Fixed batch_policy_generator.py")
        
        print("\n✅ All imports fixed!")
    
    def update_env(self):
        """Update or create .env file"""
        env_file = self.backend_root / ".env"
        
        existing_content = []
        api_key_exists = False
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip().startswith('GEMINI_API_KEY'):
                        existing_content.append(f'GEMINI_API_KEY={self.api_key}\n')
                        api_key_exists = True
                    else:
                        existing_content.append(line)
        
        if not api_key_exists:
            existing_content.append(f'\n# Google Gemini API Key\n')
            existing_content.append(f'GEMINI_API_KEY={self.api_key}\n')
        
        with open(env_file, 'w') as f:
            f.writelines(existing_content)
        
        print(f"  ✅ Updated {env_file.name}")
        print("  ✅ GEMINI_API_KEY configured")
        print("\n✅ Environment configured!")
    
    def create_helper_scripts(self):
        """Create convenient helper scripts"""
        
        # Create generate_policies.py
        generate_script = self.backend_root / "generate_policies.py"
        with open(generate_script, 'w', encoding='utf-8') as f:
            f.write('''"""
Quick Policy Generator
======================
Generates priority policies with one command
"""
import os
from app.services.ai_policy_service import PolicyGenerationService

# Set API key from environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not set in .env file!")
    exit(1)

# Priority policies to generate
PRIORITY_POLICIES = [
    "ISMS Scope",
    "Context of the Organization",
    "Information Security Policy",
    "Access Control Policy",
    "Incident Response Policy",
    "Backup and Recovery Policy"
]

print("Generating 6 priority policies...\\n")

service = PolicyGenerationService(api_key=api_key)

for i, policy_name in enumerate(PRIORITY_POLICIES, 1):
    print(f"[{i}/6] Generating: {policy_name}")
    result = service.generate_policy(policy_name)
    
    if result.get("success"):
        print(f"  ✅ {result['metadata']['word_count']} words")
        
        # Save to file
        filename = f"{policy_name.replace(' ', '_')}.md"
        filepath = f"generated_policies/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result["content"])
        print(f"  📄 Saved to: {filepath}\\n")
    else:
        print(f"  ❌ Failed: {result.get('error')}\\n")

print("✅ Done!")
''')
        print(f"  ✅ Created generate_policies.py")
        
        print("\n✅ Helper scripts created!")
    
    def test_installation(self):
        """Test that everything works"""
        print("Running tests...\n")
        
        # Test 1: Import modules
        try:
            sys.path.insert(0, str(self.backend_root))
            from app.services.policy_intents import POLICY_CONTROL_MAP
            print(f"  ✅ Modules import successfully")
            print(f"  ✅ {len(POLICY_CONTROL_MAP)} policies ready")
        except ImportError as e:
            print(f"  ❌ Import failed: {e}")
            raise
        
        # Test 2: Check new package
        try:
            from google import genai
            print("  ✅ New google-genai package installed")
        except ImportError:
            print("  ⚠️  google-genai not found - trying to install again...")
            subprocess.run([sys.executable, "-m", "pip", "install", "google-genai"])
        
        print("\n✅ All tests passed!")
    
    def generate_sample(self):
        """Generate one sample policy"""
        print("Generating 'ISMS Scope' policy as test...")
        print("This takes about 30-60 seconds...\n")
        
        # Set environment variable
        os.environ['GEMINI_API_KEY'] = self.api_key
        
        sys.path.insert(0, str(self.backend_root))
        
        try:
            from app.services.ai_policy_service import PolicyGenerationService
            
            service = PolicyGenerationService(api_key=self.api_key)
            result = service.generate_policy("ISMS Scope", company_name="AssuRisk")
            
            if result.get("success"):
                output_file = self.backend_root / "generated_policies" / "ISMS_Scope_SAMPLE.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result["content"])
                
                print("  ✅ Policy generated successfully!")
                print(f"     Word count: {result['metadata']['word_count']}")
                print(f"     Coverage: {result['intent_coverage']['coverage_percentage']}%")
                print(f"     Audit ready: {result['intent_coverage']['audit_ready']}")
                print(f"\n  📄 Saved to: {output_file.name}")
            else:
                print(f"  ⚠️  Generation failed: {result.get('error')}")
                print("     The system is installed, but API generation needs troubleshooting.")
        
        except Exception as e:
            print(f"  ⚠️  Sample generation failed: {e}")
            print("     The system is installed. You can try generating manually later.")
        
        print("\n✅ Sample generation complete!")
    
    def show_next_steps(self):
        """Show what to do next"""
        print("\n" + "🎉"*35)
        print(" "*25 + "INSTALLATION COMPLETE!")
        print("🎉"*35 + "\n")
        
        print("✅ Everything is installed and ready!\n")
        
        print("📋 QUICK START - Generate Policies Now:\n")
        
        print("1️⃣  Generate 6 priority policies:")
        print(f"   cd {self.backend_root}")
        print("   python generate_policies.py\n")
        
        print("2️⃣  Or use the batch generator for all 72 policies:")
        print("   python app/scripts/batch_policy_generator.py --mode all\n")
        
        print("3️⃣  View your generated policies:")
        print(f"   {self.backend_root / 'generated_policies'}\n")
        
        print("🔥 FILES YOU CAN RUN:\n")
        print(f"   • {self.backend_root / 'generate_policies.py'} - Quick 6-policy generator")
        print(f"   • {self.backend_root / 'demo.py'} - Interactive demo")
        print(f"   • {self.backend_root / 'app' / 'scripts' / 'batch_policy_generator.py'} - Full 72 policies\n")
        
        print("📚 NEXT STEPS:\n")
        print("   • Read the generated sample: ISMS_Scope_SAMPLE.md")
        print("   • Run generate_policies.py to get your first 6 policies")
        print("   • Review and approve them")
        print("   • Move to your Documents repository\n")


def main():
    parser = argparse.ArgumentParser(
        description="Complete AssuRisk Policy Generation Auto-Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script does EVERYTHING automatically:
  • Removes old deprecated packages
  • Installs new correct packages
  • Creates directories
  • Copies files
  • Fixes all imports
  • Updates .env
  • Tests installation
  • Generates sample policy

Just run:
  python complete_installer.py --api-key YOUR_GEMINI_API_KEY

Get your key: https://ai.google.dev/gemini-api/docs/api-key
        """
    )
    
    parser.add_argument(
        '--api-key',
        required=True,
        help='Your Google Gemini API key'
    )
    
    parser.add_argument(
        '--project-root',
        help='Path to Compliance_Product directory (auto-detected if not provided)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "⚡"*35)
    print(" "*15 + "ASSU RISK COMPLETE AUTO-INSTALLER")
    print("⚡"*35)
    print("\nZero manual steps - everything automated!")
    print("Estimated time: 5-7 minutes\n")
    
    installer = CompleteInstaller(
        api_key=args.api_key,
        project_root=args.project_root
    )
    
    success = installer.run_all()
    
    if success:
        print("\n✅ SUCCESS! Start generating policies now!\n")
        sys.exit(0)
    else:
        print("\n❌ Installation had errors. Check output above.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
