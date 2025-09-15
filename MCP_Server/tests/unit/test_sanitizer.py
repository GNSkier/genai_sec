#!/usr/bin/env python3
"""
Test script for the PII Sanitizer Agent

This script demonstrates the sanitizer functionality using sample PII data.
"""

import json
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from sanitizer_agent import SanitizerAgent


def test_sanitizer():
    """Test the sanitizer agent with various PII samples."""

    # Sample texts with PII
    test_cases = [
        {
            "name": "Log with PII",
            "text": "2024-05-21T10:00:00Z INFO User login for user_email: test@example.com from IP 192.168.1.10\n2024-05-21T10:01:00Z WARN Payment attempt for card 4111-1111-1111-1111, Exp 12/26, CVV 123\n2024-05-21T10:02:00Z INFO Contact support at 555-123-4567\n2024-05-21T10:03:00Z DEBUG User SSN 987-65-4321 flagged for verification",
        },
        {
            "name": "Email with PII",
            "text": "Dear John Smith,\n\nYour account has been created successfully. Please contact us at support@company.com or call 555-123-4567 if you have any questions.\n\nYour SSN ending in 4321 has been verified.\n\nBest regards,\nCustomer Service",
        },
        {
            "name": "Clean text (no PII)",
            "text": "The system is running normally. All services are operational. No issues detected.",
        },
        {
            "name": "Mixed content",
            "text": "User Alice Johnson (alice@example.com) made a purchase using card 4532-1234-5678-9012. Her phone number is 555-987-6543 and she lives at 123 Main Street, Anytown, ST 12345. The transaction was processed successfully.",
        },
    ]

    print("=" * 80)
    print("PII SANITIZER AGENT TEST")
    print("=" * 80)

    # Initialize the sanitizer agent
    agent = SanitizerAgent()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 50)

        # Original text
        print("ORIGINAL TEXT:")
        print(test_case["text"])
        print()

        # Detect PII
        print("PII DETECTION:")
        detection_summary = agent.detect_pii(test_case["text"])
        print(f"PII Detected: {detection_summary['total_detections'] > 0}")
        print(
            f"Categories found: {[cat for cat, count in detection_summary['categories'].items() if count > 0]}"
        )
        print(f"Unique PII items: {detection_summary['unique_pii_count']}")
        print()

        # Test different redaction types
        redaction_types = ["generic", "mask", "remove"]

        for redaction_type in redaction_types:
            print(f"REDACTION TYPE: {redaction_type.upper()}")
            result = agent.sanitize_text(test_case["text"], redaction_type)
            print("Sanitized text:")
            print(result["sanitized_text"])
            print()

        print("=" * 80)


def test_file_sanitization():
    """Test file sanitization functionality."""
    print("\n" + "=" * 80)
    print("FILE SANITIZATION TEST")
    print("=" * 80)

    # Create a test file with PII
    test_file_path = "test_pii_file.txt"
    test_content = """User Information:
Name: John Doe
Email: john.doe@example.com
Phone: 555-123-4567
SSN: 123-45-6789
Credit Card: 4532-1234-5678-9012
Address: 123 Main Street, Anytown, ST 12345

System Log:
2024-01-15 10:30:00 - User login successful
2024-01-15 10:31:00 - Payment processed for $99.99
2024-01-15 10:32:00 - Email sent to john.doe@example.com
"""

    # Write test file
    with open(test_file_path, "w") as f:
        f.write(test_content)

    print(f"Created test file: {test_file_path}")
    print("Original content:")
    print(test_content)
    print()

    # Test file sanitization
    agent = SanitizerAgent()

    try:
        # Read and sanitize file
        with open(test_file_path, "r") as f:
            content = f.read()

        result = agent.sanitize_text(content, "generic")

        # Write sanitized content
        sanitized_file_path = test_file_path + ".sanitized"
        with open(sanitized_file_path, "w") as f:
            f.write(result["sanitized_text"])

        print("Sanitized content:")
        print(result["sanitized_text"])
        print()
        print(f"Sanitized file saved as: {sanitized_file_path}")

        # Clean up
        import os

        os.remove(test_file_path)
        os.remove(sanitized_file_path)
        print("Test files cleaned up.")

    except Exception as e:
        print(f"Error during file sanitization test: {e}")


def test_detailed_report():
    """Test detailed sanitization report generation."""
    print("\n" + "=" * 80)
    print("DETAILED REPORT TEST")
    print("=" * 80)

    sample_text = "Contact John Smith at john@example.com or call 555-123-4567. His SSN is 123-45-6789 and he lives at 456 Oak Avenue."

    agent = SanitizerAgent()
    report = agent.get_sanitization_report(sample_text)

    print("Sample text:")
    print(sample_text)
    print()
    print("Detailed report:")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        test_sanitizer()
        test_file_sanitization()
        test_detailed_report()
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()
