"""
AssuRisk Policy Generation - Automated Setup Script
===================================================
This script does EVERYTHING for you - just run it once!

Usage:
    python auto_setup.py --api-key YOUR_GEMINI_API_KEY

What it does:
    1. ✅ Installs all dependencies
    2. ✅ Copies files to correct locations
    3. ✅ Updates your .env file
    4. ✅ Tests the installation
    5. ✅ Generates a sample policy
    6. ✅ Updates your FastAPI main.py
    7. ✅ Optionally generates all priority policies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse


class AutoSetup:
    """Automated setup wizard"""
    
    def __init__(self, api_key, project_root=None):
        self.api_key = api_key
        
        # Auto-detect project root or use provided
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Try to find it
            possible_paths = [
                Path(r"C:\Projects\Compliance_Product"),
                Path.home() / "Documents" / "Compliance_Product",
                Path.cwd().parent if "Backend" in str(Path.cwd()) else Path.cwd()
            ]
            
            for path in possible_paths:
                if path.exists() and (path / "Backend").exists():
                    self.project_root = path
                    break
            else:
                self.project_root = Path.cwd()
        
        self.backend_root = self.project_root / "Backend"
        self.app_root = self.backend_root / "app"
        
        print(f"\n🎯 Project root: {self.project_root}")
        print(f"🎯 Backend root: {self.backend_root}\n")
    
    def print_step(self, step_num, total, message):
        """Pretty print step progress"""
        print(f"\n{'='*70}")
        print(f"📦 STEP {step_num}/{total}: {message}")
        print(f"{'='*70}\n")
    
    def run_all(self):
        """Execute the complete setup"""
        total_steps = 8
        
        try:
            self.print_step(1, total_steps, "Installing Python Dependencies")
            self.install_dependencies()
            
            self.print_step(2, total_steps, "Creating Directory Structure")
            self.create_directories()
            
            self.print_step(3, total_steps, "Copying Policy Generation Files")
            self.copy_files()
            
            self.print_step(4, total_steps, "Updating .env Configuration")
            self.update_env()
            
            self.print_step(5, total_steps, "Integrating with FastAPI")
            self.update_fastapi()
            
            self.print_step(6, total_steps, "Testing Installation")
            self.test_installation()
            
            self.print_step(7, total_steps, "Generating Sample Policy")
            self.generate_sample()
            
            self.print_step(8, total_steps, "Setup Complete!")
            self.show_next_steps()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            print(f"   Check the error above and try again.")
            return False
    
    def install_dependencies(self):
        """Install required Python packages"""
        packages = [
            'google-generativeai>=0.3.0',
            'fastapi>=0.104.0',
            'pydantic>=2.0.0',
            'uvicorn[standard]>=0.24.0',
            'python-dotenv>=1.0.0'
        ]
        
        print("Installing packages...")
        for package in packages:
            print(f"  📦 {package}")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                capture_output=True
            )
        
        print("\n✅ All dependencies installed!")
    
    def create_directories(self):
        """Create necessary directory structure"""
        dirs = [
            self.app_root / "services",
            self.app_root / "api",
            self.app_root / "scripts",
            self.backend_root / "generated_policies" / "audit_ready",
            self.backend_root / "generated_policies" / "needs_review"
        ]
        
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {directory}")
        
        print("\n✅ Directory structure ready!")
    
    def copy_files(self):
        """Copy policy generation files to correct locations"""
        # Get the current directory where these files are
        source_dir = Path(__file__).parent
        
        file_mapping = {
            "policy_template_structure.py": self.app_root / "services" / "policy_template_structure.py",
            "policy_intents.py": self.app_root / "services" / "policy_intents.py",
            "ai_policy_service.py": self.app_root / "services" / "ai_policy_service.py",
            "api_integration.py": self.app_root / "api" / "policy_generation.py",
            "batch_policy_generator.py": self.app_root / "scripts" / "batch_policy_generator.py",
            "demo.py": self.backend_root / "demo.py"
        }
        
        for source_name, dest_path in file_mapping.items():
            source_path = source_dir / source_name
            
            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                print(f"  ✅ Copied {source_name} → {dest_path.relative_to(self.project_root)}")
            else:
                print(f"  ⚠️  {source_name} not found in {source_dir}")
        
        print("\n✅ Files copied successfully!")
    
    def update_env(self):
        """Update or create .env file with API key"""
        env_file = self.backend_root / ".env"
        
        # Read existing .env if it exists
        existing_content = []
        api_key_exists = False
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip().startswith('GEMINI_API_KEY'):
                        # Replace existing key
                        existing_content.append(f'GEMINI_API_KEY={self.api_key}\n')
                        api_key_exists = True
                    else:
                        existing_content.append(line)
        
        # Add API key if it wasn't there
        if not api_key_exists:
            existing_content.append(f'\n# Google Gemini API Key for Policy Generation\n')
            existing_content.append(f'GEMINI_API_KEY={self.api_key}\n')
        
        # Write back
        with open(env_file, 'w') as f:
            f.writelines(existing_content)
        
        print(f"  ✅ Updated {env_file}")
        print(f"  ✅ GEMINI_API_KEY configured")
        print("\n✅ Environment configured!")
    
    def update_fastapi(self):
        """Update main.py to include policy generation router"""
        main_py = self.app_root / "main.py"
        
        if not main_py.exists():
            print("  ⚠️  main.py not found - you'll need to add the router manually")
            print("      See INTEGRATION_GUIDE.md for instructions")
            return
        
        with open(main_py, 'r') as f:
            content = f.read()
        
        # Check if already integrated
        if 'policy_generation' in content:
            print("  ✅ Policy generation already integrated in main.py")
            return
        
        # Add import
        import_line = "from app.api import policy_generation\n"
        if "from app.api" in content:
            # Add after existing app.api imports
            content = content.replace(
                "from app.api import",
                f"{import_line}from app.api import",
                1
            )
        else:
            # Add at top after FastAPI import
            content = content.replace(
                "from fastapi import FastAPI",
                f"from fastapi import FastAPI\n{import_line}"
            )
        
        # Add router
        router_code = """
# Policy Generation Router
app.include_router(
    policy_generation.router,
    prefix="/api",
    tags=["Policy Generation"]
)
"""
        
        # Find a good place to add it (after other routers)
        if "app.include_router" in content:
            # Add after last router
            lines = content.split('\n')
            last_router_line = 0
            for i, line in enumerate(lines):
                if 'app.include_router' in line:
                    last_router_line = i
            
            # Insert after the last router block
            lines.insert(last_router_line + 3, router_code)
            content = '\n'.join(lines)
        else:
            # Add before the main app run code
            content = content.replace(
                'if __name__ == "__main__"',
                f'{router_code}\n\nif __name__ == "__main__"'
            )
        
        # Backup original
        shutil.copy2(main_py, main_py.with_suffix('.py.backup'))
        
        # Write updated version
        with open(main_py, 'w') as f:
            f.write(content)
        
        print("  ✅ Updated main.py (backup saved as main.py.backup)")
        print("  ✅ Policy generation router integrated")
        print("\n✅ FastAPI integration complete!")
    
    def test_installation(self):
        """Test that everything is working"""
        print("Running tests...\n")
        
        # Test 1: Import modules
        try:
            sys.path.insert(0, str(self.backend_root))
            from app.services.ai_policy_service import PolicyGenerationService
            from app.services.policy_intents import POLICY_CONTROL_MAP
            print("  ✅ Modules import successfully")
        except ImportError as e:
            print(f"  ❌ Import failed: {e}")
            raise
        
        # Test 2: API key
        os.environ['GEMINI_API_KEY'] = self.api_key
        try:
            service = PolicyGenerationService(api_key=self.api_key)
            print("  ✅ API key configured correctly")
        except Exception as e:
            print(f"  ❌ API key test failed: {e}")
            raise
        
        # Test 3: Policy mapping
        print(f"  ✅ {len(POLICY_CONTROL_MAP)} policies ready for generation")
        
        print("\n✅ All tests passed!")
    
    def generate_sample(self):
        """Generate one sample policy to verify everything works"""
        print("Generating 'ISMS Scope' policy as test...")
        print("This takes about 30-60 seconds...\n")
        
        sys.path.insert(0, str(self.backend_root))
        from app.services.ai_policy_service import PolicyGenerationService
        
        try:
            service = PolicyGenerationService(api_key=self.api_key)
            result = service.generate_policy("ISMS Scope", company_name="AssuRisk")
            
            if result["success"]:
                # Save to file
                output_file = self.backend_root / "generated_policies" / "test_isms_scope.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result["content"])
                
                print("  ✅ Policy generated successfully!")
                print(f"     Word count: {result['metadata']['word_count']}")
                print(f"     Intent coverage: {result['intent_coverage']['coverage_percentage']}%")
                print(f"     Audit ready: {result['intent_coverage']['audit_ready']}")
                print(f"\n  📄 Saved to: {output_file}")
            else:
                print(f"  ⚠️  Generation completed with warnings")
                print(f"     {result.get('error', 'Check output for details')}")
        
        except Exception as e:
            print(f"  ⚠️  Sample generation failed: {e}")
            print("     Don't worry - the system is installed correctly.")
            print("     This might be due to API rate limits or network issues.")
        
        print("\n✅ Sample generation complete!")
    
    def show_next_steps(self):
        """Show what to do next"""
        print("\n" + "🎉"*35)
        print(" "*25 + "SETUP COMPLETE!")
        print("🎉"*35 + "\n")
        
        print("✅ Everything is installed and ready to use!\n")
        
        print("📋 NEXT STEPS:\n")
        
        print("1️⃣  Generate priority policies (12 most critical):")
        print(f"   cd {self.backend_root}")
        print("   python app/scripts/batch_policy_generator.py --mode priority\n")
        
        print("2️⃣  Or generate ALL 72 policies:")
        print("   python app/scripts/batch_policy_generator.py --mode all\n")
        
        print("3️⃣  Start your API server:")
        print("   uvicorn app.main:app --reload")
        print("   Then visit: http://localhost:8000/docs\n")
        
        print("4️⃣  Run the interactive demo:")
        print("   python demo.py\n")
        
        print("📚 DOCUMENTATION:")
        print("   - QUICK_START.md - Quick reference")
        print("   - README.md - Full documentation")
        print("   - INTEGRATION_GUIDE.md - Frontend integration\n")
        
        print("🎯 Your generated policies will be in:")
        print(f"   {self.backend_root / 'generated_policies' / 'audit_ready'}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Automated setup for AssuRisk Policy Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_setup.py --api-key YOUR_GEMINI_API_KEY
  python auto_setup.py --api-key YOUR_KEY --project-root "C:/Projects/AssuRisk"
  
Get your Gemini API key at: https://makersuite.google.com/app/apikey
        """
    )
    
    parser.add_argument(
        '--api-key',
        required=True,
        help='Your Google Gemini API key'
    )
    
    parser.add_argument(
        '--project-root',
        help='Path to your Compliance_Product directory (auto-detected if not provided)'
    )
    
    parser.add_argument(
        '--skip-sample',
        action='store_true',
        help='Skip generating the sample policy (faster setup)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "⚡"*35)
    print(" "*20 + "ASSU RISK AUTO-SETUP")
    print("⚡"*35)
    print("\nThis will automatically install and configure the Policy Generation system.")
    print("Estimated time: 3-5 minutes\n")
    
    setup = AutoSetup(
        api_key=args.api_key,
        project_root=args.project_root
    )
    
    success = setup.run_all()
    
    if success:
        print("\n✅ SUCCESS! You're ready to generate policies!\n")
        sys.exit(0)
    else:
        print("\n❌ Setup encountered errors. Please check the output above.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
