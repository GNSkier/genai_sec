#!/usr/bin/env python3
"""
Sanitizer Agent for MCP Server

This module provides PII sanitization capabilities using the enhanced PII detection
from the PII_testing module. It can redact sensitive information from text input.
"""

import sys
import os
import re
import json
from pathlib import Path

# Add the PII_testing directory to the path
pii_testing_path = Path(__file__).parent.parent.parent.parent / "PII_testing"
sys.path.insert(0, str(pii_testing_path))

try:
    from pii_logging import Enhanced_PII_Logging
except ImportError as e:
    print(f"Error importing PII detection module: {e}", file=sys.stderr)
    raise


class SanitizerAgent:
    """
    A sanitizer agent that detects and redacts PII from text input.
    """

    def __init__(
        self, enable_proximity=True, enable_graph=True, window_size=50
    ):
        """
        Initialize the sanitizer agent.

        Args:
            enable_proximity (bool): Enable proximity-based PII detection
            enable_graph (bool): Enable graph-based PII detection
            window_size (int): Window size for proximity analysis
        """
        self.enable_proximity = enable_proximity
        self.enable_graph = enable_graph
        self.window_size = window_size

        # PII patterns for redaction
        self.pii_patterns = {
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PHONE": r"\b(?:\+?1[\s.-]?)?(\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b",
            "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "Credit_Card": r"\b\d{4}-\d{4}-\d{4}-\d{4}\b|\b\d{16}\b",
            "Expiration_Date": r"\b\d{2}/\d{2}\b",
            "CVV": r"(?i)(cvv|cvc|cid|security\s+code)[\s:]*['\"]?\d{3,4}['\"]?",
            "Driver's_License": r"(?i)\b(?:[A-Z]{1,3}\d{4,8}|[A-Z]\d{6,12}|\d{3}[A-Z]{2}\d{4})\b",
            "IPv4_Address": r"\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}\b",
            "IPV6_Address": r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|:(:[0-9a-fA-F]{1,4}){1,7}|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|::((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|(::ffff|::)ffff:([0-9]{1,3}\.){3}[0-9]{1,3}",
        }

        # Redaction patterns for different PII types
        self.redaction_patterns = {
            "EMAIL": "[REDACTED_EMAIL]",
            "PHONE": "[REDACTED_PHONE]",
            "SSN": "[REDACTED_SSN]",
            "Credit_Card": "[REDACTED_CREDIT_CARD]",
            "Expiration_Date": "[REDACTED_EXP_DATE]",
            "CVV": "[REDACTED_CVV]",
            "Driver's_License": "[REDACTED_DL]",
            "IPv4_Address": "[REDACTED_IP]",
            "IPV6_Address": "[REDACTED_IPV6]",
            "Names": "[REDACTED_NAME]",
            "Addresses": "[REDACTED_ADDRESS]",
            "Dates": "[REDACTED_DATE]",
            "Sensitive_Words": "[REDACTED_ORG]",
        }

    def detect_pii(self, text):
        """
        Detect PII in the given text using the enhanced PII detection.

        Args:
            text (str): Text to analyze for PII

        Returns:
            dict: Detection summary with categories and details
        """
        detector = Enhanced_PII_Logging(
            text,
            output=False,
            replace=False,
            log_type="Mask",
            debug=False,
            enable_proximity=self.enable_proximity,
            enable_graph=self.enable_graph,
            window_size=self.window_size,
        )

        return detector.get_detection_summary()

    def sanitize_text(self, text, redaction_type="generic"):
        """
        Sanitize text by redacting detected PII.

        Args:
            text (str): Text to sanitize
            redaction_type (str): Type of redaction ("generic", "mask", "remove")

        Returns:
            dict: Contains sanitized text and detection details
        """
        # First detect PII
        detection_summary = self.detect_pii(text)

        if detection_summary["total_detections"] == 0:
            return {
                "sanitized_text": text,
                "original_text": text,
                "pii_detected": False,
                "detection_summary": detection_summary,
                "redaction_type": redaction_type,
            }

        # Apply redaction based on type
        sanitized_text = text

        if redaction_type == "generic":
            sanitized_text = self._apply_generic_redaction(
                text, detection_summary
            )
        elif redaction_type == "mask":
            sanitized_text = self._apply_mask_redaction(text, detection_summary)
        elif redaction_type == "remove":
            sanitized_text = self._apply_removal_redaction(
                text, detection_summary
            )

        return {
            "sanitized_text": sanitized_text,
            "original_text": text,
            "pii_detected": True,
            "detection_summary": detection_summary,
            "redaction_type": redaction_type,
        }

    def _apply_generic_redaction(self, text, detection_summary):
        """Apply generic redaction using pattern matching."""
        sanitized_text = text

        # Apply regex-based redaction for each PII type
        for category, pattern in self.pii_patterns.items():
            if (
                category in detection_summary["categories"]
                and detection_summary["categories"][category] > 0
            ):
                redaction_text = self.redaction_patterns.get(
                    category, "[REDACTED]"
                )
                sanitized_text = re.sub(
                    pattern, redaction_text, sanitized_text, flags=re.IGNORECASE
                )

        return sanitized_text

    def _apply_mask_redaction(self, text, detection_summary):
        """Apply mask redaction (e.g., john@example.com -> j***@e***.com)."""
        sanitized_text = text

        # Email masking
        email_pattern = (
            r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+)\.([A-Z|a-z]{2,})\b"
        )

        def mask_email(match):
            local, domain, tld = match.groups()
            return f"{local[0]}***@{domain[0]}***.{tld[0]}***"

        sanitized_text = re.sub(email_pattern, mask_email, sanitized_text)

        # Phone masking
        phone_pattern = (
            r"\b(?:\+?1[\s.-]?)?(\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b"
        )

        def mask_phone(match):
            phone = match.group()
            if len(phone) >= 10:
                return phone[:3] + "***" + phone[-4:]
            return "***"

        sanitized_text = re.sub(phone_pattern, mask_phone, sanitized_text)

        # SSN masking
        ssn_pattern = r"\b(\d{3})-(\d{2})-(\d{4})\b"

        def mask_ssn(match):
            return "***-**-****"

        sanitized_text = re.sub(ssn_pattern, mask_ssn, sanitized_text)

        # Credit card masking
        cc_pattern = r"\b\d{4}-\d{4}-\d{4}-\d{4}\b|\b\d{16}\b"

        def mask_cc(match):
            cc = match.group().replace("-", "")
            if len(cc) == 16:
                return cc[:4] + "-****-****-" + cc[-4:]
            return "****-****-****-****"

        sanitized_text = re.sub(cc_pattern, mask_cc, sanitized_text)

        return sanitized_text

    def _apply_removal_redaction(self, text, detection_summary):
        """Apply removal redaction (remove PII entirely)."""
        sanitized_text = text

        # Remove all PII patterns
        for category, pattern in self.pii_patterns.items():
            if (
                category in detection_summary["categories"]
                and detection_summary["categories"][category] > 0
            ):
                sanitized_text = re.sub(
                    pattern, "", sanitized_text, flags=re.IGNORECASE
                )

        # Clean up extra whitespace
        sanitized_text = re.sub(r"\s+", " ", sanitized_text).strip()

        return sanitized_text

    def get_sanitization_report(self, text):
        """
        Get a detailed report of what would be sanitized without actually sanitizing.

        Args:
            text (str): Text to analyze

        Returns:
            dict: Detailed sanitization report
        """
        detection_summary = self.detect_pii(text)

        report = {
            "original_text": text,
            "pii_detected": detection_summary["total_detections"] > 0,
            "detection_summary": detection_summary,
            "categories_found": [
                cat
                for cat, count in detection_summary["categories"].items()
                if count > 0
            ],
            "total_unique_pii": detection_summary["unique_pii_count"],
            "detailed_findings": detection_summary["detailed_findings"],
        }

        return report


def main():
    """CLI interface for the sanitizer agent."""
    import argparse

    parser = argparse.ArgumentParser(description="PII Sanitizer Agent")
    parser.add_argument("text", help="Text to sanitize")
    parser.add_argument(
        "--redaction-type",
        choices=["generic", "mask", "remove"],
        default="generic",
        help="Type of redaction to apply",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only generate a report without sanitizing",
    )
    parser.add_argument(
        "--no-proximity", action="store_true", help="Disable proximity analysis"
    )
    parser.add_argument(
        "--no-graph", action="store_true", help="Disable graph analysis"
    )

    args = parser.parse_args()

    agent = SanitizerAgent(
        enable_proximity=not args.no_proximity, enable_graph=not args.no_graph
    )

    if args.report_only:
        report = agent.get_sanitization_report(args.text)
        print(json.dumps(report, indent=2))
    else:
        result = agent.sanitize_text(args.text, args.redaction_type)
        print("Original text:")
        print(result["original_text"])
        print("\nSanitized text:")
        print(result["sanitized_text"])
        print(f"\nPII detected: {result['pii_detected']}")
        if result["pii_detected"]:
            print(
                f"Categories found: {[cat for cat, count in result['detection_summary']['categories'].items() if count > 0]}"
            )


if __name__ == "__main__":
    main()
