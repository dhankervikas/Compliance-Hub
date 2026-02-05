from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class EvidenceData:
    """Standardized format for collected evidence"""
    def __init__(
        self, 
        content: str, 
        metadata: Dict[str, Any], 
        status: str = "success",
        error: Optional[str] = None
    ):
        self.content = content
        self.metadata = metadata
        self.status = status
        self.error = error
        self.collected_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "metadata": self.metadata,
            "status": self.status,
            "error": self.error,
            "collected_at": self.collected_at.isoformat()
        }

class BaseCollector(ABC):
    """
    Abstract Base Class for all Evidence Collectors.
    All collectors must implement the `collect` method.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the collector (e.g., 'PasswordPolicyCollector')"""
        pass
    
    @property
    @abstractmethod
    def supported_controls(self) -> list[str]:
        """List of control IDs this collector supports (e.g., ['A.5.17', 'A.9.4.3'])"""
        pass

    @abstractmethod
    def collect(self, control_id: str) -> EvidenceData:
        """
        Execute the collection logic.
        Expected to return EvidenceData object.
        """
        pass
    
    def validate_environment(self) -> bool:
        """
        Optional: Check if environment allows this collector to run.
        e.g., check if 'aws' cli is installed.
        """
        return True
