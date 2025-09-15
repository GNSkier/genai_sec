#!/usr/bin/env python3
"""
Basic Usage Examples

This shows how to use the sanitizer system programmatically.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.agent.sanitizer_agent import SanitizerAgent


def basic_examples():
    """Basic sanitizer examples."""
    print("=" * 60)
    print("🧹 BASIC SANITIZER EXAMPLES")
    print("=" * 60)
    print()

    # Initialize sanitizer
    agent = SanitizerAgent()

    # Example 1: Detect PII
    print("1. Detecting PII:")
    text = "Contact john@example.com or call 555-123-4567"
    result = agent.detect_pii(text)
    print(f"   Text: {text}")
    print(f"   PII detected: {result['total_detections']} items")
    print(f"   Categories: {result['categories']}")
    print()

    # Example 2: Generic redaction
    print("2. Generic redaction:")
    result = agent.sanitize_text(text, "generic")
    print(f"   Original: {text}")
    print(f"   Sanitized: {result['sanitized_text']}")
    print()

    # Example 3: Mask redaction
    print("3. Mask redaction:")
    result = agent.sanitize_text(text, "mask")
    print(f"   Original: {text}")
    print(f"   Sanitized: {result['sanitized_text']}")
    print()

    # Example 4: Remove redaction
    print("4. Remove redaction:")
    text2 = "My SSN is 123-45-6789"
    result = agent.sanitize_text(text2, "remove")
    print(f"   Original: {text2}")
    print(f"   Sanitized: {result['sanitized_text']}")
    print()

    print("✅ Basic examples completed!")


if __name__ == "__main__":
    basic_examples()
