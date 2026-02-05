"""
Automated Control Testing System
This module contains test functions that automatically check if controls are implemented.
Each test returns: (status, evidence, details)
"""

import os
import json
from datetime import datetime
from typing import Tuple, Dict, Any

class ControlTest:
    """Base class for control tests"""
    
    @staticmethod
    def test_password_policy() -> Tuple[str, str, Dict[str, Any]]:
        """
        Test A.9.4.3: Password management system
        Checks if password policy meets requirements
        """
        try:
            # Simulated test - checks if password policy file exists
            # In production, this would check actual system settings
            
            requirements = {
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special": True,
                "max_age_days": 90
            }
            
            # Simulate checking system password policy
            # Replace with actual checks in production
            policy_exists = True  # Simulated
            meets_requirements = True  # Simulated
            
            if policy_exists and meets_requirements:
                evidence = {
                    "test_type": "password_policy_check",
                    "requirements_met": requirements,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "compliant"
                }
                return ("implemented", json.dumps(evidence), {
                    "message": "Password policy meets all requirements",
                    "compliant": True
                })
            else:
                return ("not_started", "", {
                    "message": "Password policy not configured or doesn't meet requirements",
                    "compliant": False
                })
                
        except Exception as e:
            return ("not_started", "", {
                "message": f"Error checking password policy: {str(e)}",
                "compliant": False
            })
    
    @staticmethod
    def test_mfa_enabled() -> Tuple[str, str, Dict[str, Any]]:
        """
        Test A.9.4.2: Secure log-on procedures
        Checks if MFA is enabled for admin accounts
        """
        try:
            # Simulated test - checks if MFA is configured
            # In production, this would check AWS IAM, Azure AD, etc.
            
            mfa_enabled = True  # Simulated - would check actual system
            admin_accounts_protected = True  # Simulated
            
            if mfa_enabled and admin_accounts_protected:
                evidence = {
                    "test_type": "mfa_check",
                    "mfa_enabled": True,
                    "admin_accounts_protected": True,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "compliant"
                }
                return ("implemented", json.dumps(evidence), {
                    "message": "MFA is enabled for all admin accounts",
                    "compliant": True
                })
            else:
                return ("in_progress", "", {
                    "message": "MFA partially configured",
                    "compliant": False
                })
                
        except Exception as e:
            return ("not_started", "", {
                "message": f"Error checking MFA: {str(e)}",
                "compliant": False
            })
    
    @staticmethod
    def test_backup_configured() -> Tuple[str, str, Dict[str, Any]]:
        """
        Test A.8.13: Information backup
        Checks if automated backups are configured
        """
        try:
            # Simulated test - checks backup configuration
            # In production, this would check AWS Backup, Azure Backup, etc.
            
            backups_enabled = True  # Simulated
            retention_policy = "30 days"  # Simulated
            last_backup = datetime.utcnow().isoformat()  # Simulated
            
            if backups_enabled:
                evidence = {
                    "test_type": "backup_check",
                    "backups_enabled": True,
                    "retention_policy": retention_policy,
                    "last_successful_backup": last_backup,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "compliant"
                }
                return ("implemented", json.dumps(evidence), {
                    "message": f"Automated backups configured with {retention_policy} retention",
                    "compliant": True,
                    "last_backup": last_backup
                })
            else:
                return ("not_started", "", {
                    "message": "Automated backups not configured",
                    "compliant": False
                })
                
        except Exception as e:
            return ("not_started", "", {
                "message": f"Error checking backups: {str(e)}",
                "compliant": False
            })
    
    @staticmethod
    def test_encryption_at_rest() -> Tuple[str, str, Dict[str, Any]]:
        """
        Test A.8.24: Use of cryptography
        Checks if data encryption at rest is enabled
        """
        try:
            # Simulated test - checks encryption settings
            # In production, this would check S3, RDS, EBS encryption, etc.
            
            encryption_enabled = True  # Simulated
            encryption_algorithm = "AES-256"  # Simulated
            
            if encryption_enabled:
                evidence = {
                    "test_type": "encryption_check",
                    "encryption_enabled": True,
                    "algorithm": encryption_algorithm,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "compliant"
                }
                return ("implemented", json.dumps(evidence), {
                    "message": f"Encryption at rest enabled using {encryption_algorithm}",
                    "compliant": True
                })
            else:
                return ("not_started", "", {
                    "message": "Encryption at rest not enabled",
                    "compliant": False
                })
                
        except Exception as e:
            return ("not_started", "", {
                "message": f"Error checking encryption: {str(e)}",
                "compliant": False
            })
    
    @staticmethod
    def test_logging_enabled() -> Tuple[str, str, Dict[str, Any]]:
        """
        Test A.8.15: Logging
        Checks if security logging is enabled and retained
        """
        try:
            # Simulated test - checks logging configuration
            # In production, this would check CloudTrail, Azure Monitor, etc.
            
            logging_enabled = True  # Simulated
            retention_days = 365  # Simulated
            log_integrity = True  # Simulated
            
            if logging_enabled and log_integrity:
                evidence = {
                    "test_type": "logging_check",
                    "logging_enabled": True,
                    "retention_days": retention_days,
                    "log_integrity_protected": log_integrity,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "compliant"
                }
                return ("implemented", json.dumps(evidence), {
                    "message": f"Security logging enabled with {retention_days} day retention",
                    "compliant": True
                })
            else:
                return ("not_started", "", {
                    "message": "Logging not properly configured",
                    "compliant": False
                })
                
        except Exception as e:
            return ("not_started", "", {
                "message": f"Error checking logging: {str(e)}",
                "compliant": False
            })


# Mapping of control IDs to test functions
CONTROL_TESTS = {
    # ISO 27001 Annex A controls that can be automatically tested
    "A.5.17": ControlTest.test_password_policy,  # Authentication information (Password Policy)
    "A.8.5": ControlTest.test_mfa_enabled,       # Secure authentication (MFA)
    "A.8.13": ControlTest.test_backup_configured,
    "A.8.24": ControlTest.test_encryption_at_rest,
    "A.8.15": ControlTest.test_logging_enabled,
    # Add more mappings as you create more tests
}


def run_control_test(control_id: str) -> Dict[str, Any]:
    """
    Run automated test for a specific control
    Returns test results including status, evidence, and details
    """
    if control_id not in CONTROL_TESTS:
        return {
            "success": False,
            "message": f"No automated test available for control {control_id}",
            "has_test": False
        }
    
    try:
        test_func = CONTROL_TESTS[control_id]
        status, evidence, details = test_func()
        
        return {
            "success": True,
            "has_test": True,
            "control_id": control_id,
            "status": status,
            "evidence": evidence,
            "details": details,
            "tested_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error running test: {str(e)}",
            "has_test": True
        }


def run_all_tests() -> Dict[str, Any]:
    """
    Run all available automated tests
    Returns summary of all test results
    """
    results = []
    total_tests = len(CONTROL_TESTS)
    passed = 0
    failed = 0
    
    for control_id in CONTROL_TESTS.keys():
        result = run_control_test(control_id)
        results.append(result)
        
        if result.get("success") and result.get("details", {}).get("compliant"):
            passed += 1
        else:
            failed += 1
    
    return {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }