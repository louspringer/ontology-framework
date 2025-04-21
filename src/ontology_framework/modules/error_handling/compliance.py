from typing import Dict, Any
from .types import ComplianceLevel

class ComplianceHandler:
    """Class for handling compliance tracking and reporting."""
    
    def __init__(self) -> None:
        """Initialize compliance handler with default standards."""
        self.compliance: Dict[str, Dict[str, Any]] = {
            "ISO27001": {
                "level": ComplianceLevel.NOT_STARTED,
                "requirements": {
                    "access_control": False,
                    "encryption": False,
                    "audit_logging": False,
                    "incident_management": False,
                    "risk_assessment": False
                }
            },
            "GDPR": {
                "level": ComplianceLevel.NOT_STARTED,
                "requirements": {
                    "data_protection": False,
                    "consent_management": False,
                    "data_portability": False,
                    "right_to_be_forgotten": False,
                    "privacy_by_design": False
                }
            },
            "HIPAA": {
                "level": ComplianceLevel.NOT_STARTED,
                "requirements": {
                    "phi_protection": False,
                    "access_controls": False,
                    "audit_controls": False,
                    "integrity_controls": False,
                    "transmission_security": False
                }
            }
        }

    def update_compliance(self, standard: str, requirement: str, status: bool) -> None:
        """Update compliance status for a specific requirement."""
        if standard in self.compliance and requirement in self.compliance[standard]["requirements"]:
            self.compliance[standard]["requirements"][requirement] = status
            self._update_compliance_level(standard)

    def _update_compliance_level(self, standard: str) -> None:
        """Update overall compliance level based on requirements status."""
        if standard in self.compliance:
            requirements = self.compliance[standard]["requirements"]
            if all(requirements.values()):
                self.compliance[standard]["level"] = ComplianceLevel.FULL
            elif any(requirements.values()):
                self.compliance[standard]["level"] = ComplianceLevel.PARTIAL
            else:
                self.compliance[standard]["level"] = ComplianceLevel.NOT_STARTED

    def get_compliance_report(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed compliance report."""
        report: Dict[str, Dict[str, Any]] = {}
        for standard, data in self.compliance.items():
            report[standard] = {
                "level": data["level"],
                "requirements": data["requirements"],
                "status": "COMPLIANT" if data["level"] == ComplianceLevel.FULL else "NON_COMPLIANT"
            }
        return report

    def check_compliance(self, standard: str) -> bool:
        """Check if a specific standard is fully compliant."""
        return (standard in self.compliance and 
                self.compliance[standard]["level"] == ComplianceLevel.FULL) 