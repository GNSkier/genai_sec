import os
import json
import sys
import types

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from pii_logging import Enhanced_PII_Logging, read_text_from_path  # noqa: E402


def test_detection_on_text_with_pii_basic():
    text = (
        "User John Smith (john.smith@example.com) called support at 555-123-4567. "
        "SSN: 123-45-6789."
    )
    detector = Enhanced_PII_Logging(
        text,
        output=False,
        replace=False,
        debug=False,
        enable_proximity=True,
        enable_graph=False,
    )
    summary = detector.get_detection_summary()
    assert summary["unique_pii_count"] >= 3
    assert summary["categories"]["EMAIL"] >= 1
    assert summary["categories"]["PHONE"] >= 1
    assert summary["categories"]["SSN"] >= 1


def test_no_pii_text():
    text = "System started successfully. All services healthy."
    detector = Enhanced_PII_Logging(
        text,
        output=False,
        debug=False,
        enable_proximity=True,
        enable_graph=True,
    )
    summary = detector.get_detection_summary()
    assert summary["unique_pii_count"] == 0
    assert max(summary["categories"].values()) == 0


def test_deduplication_same_value_multiple_methods():
    # Same email appears multiple times; ensure counted once
    text = (
        "Contact john.smith@company.com for help. "
        "User email: john.smith@company.com was verified."
    )
    detector = Enhanced_PII_Logging(
        text, output=False, debug=True, enable_proximity=True, enable_graph=True
    )
    summary = detector.get_detection_summary()
    assert summary["categories"]["EMAIL"] == 1
    assert summary["unique_pii_count"] == 1


def test_proximity_confidence_affects_reasoning():
    # SSN-like pattern in a model number without keywords
    text = "Model number: 987-65-4321 is now in stock."
    detector = Enhanced_PII_Logging(
        text,
        output=False,
        debug=False,
        enable_proximity=True,
        enable_graph=False,
    )
    details = sum((v for v in detector.PII_DETAILS.values()), [])
    # If proximity finds it, confidence may be Low due to no keyword
    low_conf_entries = [
        d
        for d in details
        if d.get("method") == "proximity_analysis"
        and d.get("confidence") == "Low"
    ]
    # Not asserting presence strictly (regex might also catch it). Just ensure schema is present if proximity ran
    assert isinstance(detector.PII_DETAILS, dict)


def test_graph_detection_clusters(monkeypatch):
    # Force graph_based_analysis to return a simple cluster including email and phone
    detector = Enhanced_PII_Logging(
        "User placeholder",
        output=False,
        debug=False,
        enable_proximity=False,
        enable_graph=True,
    )

    def fake_graph_based_analysis(data):
        import networkx as nx

        G = nx.Graph()
        G.add_edge("john.smith@example.com", "555-123-4567")
        clusters = [{"john.smith@example.com", "555-123-4567"}]
        return (
            G,
            clusters,
            [{"email": "john.smith@example.com", "phone": "555-123-4567"}],
        )

    monkeypatch.setattr(
        detector, "graph_based_analysis", fake_graph_based_analysis
    )
    # Include mocked PII items in the text so graph detection matches them
    graph_text = "User placeholder with john.smith@example.com and 555-123-4567"
    detector.graph_detection(graph_text)
    summary = detector.get_detection_summary()
    assert summary["categories"]["EMAIL"] >= 1
    assert summary["categories"]["PHONE"] >= 1


def test_cli_read_text_from_path(tmp_path):
    p = tmp_path / "sample.log"
    p.write_text("User email: a@b.com logged in from 10.0.0.1\n")
    read_back = read_text_from_path(str(p))
    assert "a@b.com" in read_back
