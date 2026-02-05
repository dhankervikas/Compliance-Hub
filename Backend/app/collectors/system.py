import subprocess
import platform
from app.collectors.base import BaseCollector, EvidenceData

class PasswordPolicyCollector(BaseCollector):
    
    @property
    def name(self) -> str:
        return "PasswordPolicyCollector"

    @property
    def supported_controls(self) -> list[str]:
        # Maps to ISO A.5.17 (Authentication Info) and A.9.4.3 (Password Mgmt)
        # Also SOC 2 CC6.1 (Logical Access)
        return ["A.5.17", "A.9.4.3", "CC6.1"]
    
    def validate_environment(self) -> bool:
        return platform.system() == "Windows"

    def collect(self, control_id: str) -> EvidenceData:
        if not self.validate_environment():
            return EvidenceData(
                content="Collection Skipped: Host is not Windows.",
                metadata={"os": platform.system()},
                status="skipped",
                error="Incompatible OS"
            )
        
        try:
            # Run the command
            result = subprocess.run(
                ["net", "accounts"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            raw_output = result.stdout
            parsed_data = self._parse_net_accounts(raw_output)
            
            # Additional context
            metadata = {
                "command": "net accounts",
                "os": platform.system(),
                "parsed_policy": parsed_data
            }
            
            return EvidenceData(
                content=raw_output,
                metadata=metadata,
                status="success"
            )
            
        except subprocess.CalledProcessError as e:
            return EvidenceData(
                content=f"Command failed: {e.stderr}",
                metadata={"command": "net accounts"},
                status="failed",
                error=str(e)
            )
        except Exception as e:
             return EvidenceData(
                content=f"Unexpected error: {str(e)}",
                metadata={},
                status="error",
                error=str(e)
            )

    def _parse_net_accounts(self, output: str) -> dict:
        """Parses the rough text output of 'net accounts' into a dictionary"""
        data = {}
        for line in output.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()
        return data
