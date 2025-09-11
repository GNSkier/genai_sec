#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import threading

try:
    import spacy
except Exception as e:
    print(
        "Error: spaCy is required. Install with: pip install spacy && python -m spacy download en_core_web_sm",
        file=sys.stderr,
    )
    raise

try:
    import networkx as nx
except Exception as e:
    print(
        "Error: networkx is required. Install with: pip install networkx",
        file=sys.stderr,
    )
    raise


def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        print(
            "Missing spaCy model 'en_core_web_sm'. Installing...",
            file=sys.stderr,
        )
        import subprocess

        try:
            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return spacy.load("en_core_web_sm")
        except Exception as e:
            print(
                "Failed to load or install spaCy model 'en_core_web_sm'.",
                file=sys.stderr,
            )
            raise


nlp = load_spacy_model()


class Enhanced_PII_Logging:
    def __init__(
        self,
        data,
        output=False,
        replace=False,
        log_type="Block",
        debug=False,
        enable_proximity=True,
        enable_graph=True,
        window_size=50,
    ):
        self.data = data
        self.output = output
        self.replace = replace
        self.log_type = log_type
        self.debug = debug
        self.enable_proximity = enable_proximity
        self.enable_graph = enable_graph
        self.window_size = window_size

        self.PII_KEYWORD = {}
        self.PII_PATTERN = {
            "EMAIL": 0,
            "PHONE": 0,
            "SSN": 0,
            "Credit_Card": 0,
            "Expiration_Date": 0,
            "CVV": 0,
            "Driver's_License": 0,
            "Names": 0,
            "Dates": 0,
            "Addresses": 0,
            "Sensitive_Words": 0,
            "IPV6_Address": 0,
            "IPv4_Address": 0,
        }

        self.PII_OUTPUT = {}
        self.PII_DETAILS = {}
        self.UNIQUE_PII = set()

        length = data.split(". ")
        for line_num in range(len(length)):
            self.PII_OUTPUT[line_num] = []
            self.PII_DETAILS[line_num] = []

        self.proximity_keywords = {
            "SSN": ["ssn", "social security", "social", "ss#", "ss #"],
            "EMAIL": ["email", "e-mail", "mail", "contact"],
            "PHONE": ["phone", "telephone", "call", "contact", "mobile"],
            "Credit_Card": [
                "credit card",
                "card number",
                "cc",
                "visa",
                "mastercard",
            ],
            "CVV": ["cvv", "cvc", "security code", "verification code"],
            "Driver's_License": ["driver", "license", "dl", "driving"],
            "Addresses": [
                "address",
                "street",
                "avenue",
                "road",
                "city",
                "state",
                "zip",
            ],
            "Names": ["name", "person", "individual", "customer", "user"],
            "Dates": ["date", "birth", "dob", "born", "created", "modified"],
        }

        self.output_function(data)

    def extract_match(self, pattern, text):
        match = re.search(pattern, text)
        return match.group() if match else None

    def redaction(self, flags, text):
        for index, flag in flags.items():
            for word in flag:
                text = re.sub(re.escape(word), "REDACTED", text)
        return text

    def proximity_analysis(self, text, pattern, keywords, category):
        findings = []
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            start, end = match.span()
            window_start = max(0, start - self.window_size)
            window_end = min(len(text), end + self.window_size)
            context_window = text[window_start:window_end]
            found_keyword = None
            for keyword in keywords:
                if re.search(
                    r"\b" + re.escape(keyword) + r"\b",
                    context_window,
                    re.IGNORECASE,
                ):
                    found_keyword = keyword
                    break
            confidence = "High" if found_keyword else "Low"
            findings.append(
                {
                    "value": match.group(0),
                    "confidence": confidence,
                    "method": "proximity_analysis",
                    "reason": (
                        f"Found nearby keyword: '{found_keyword}'"
                        if found_keyword
                        else "No nearby keywords found."
                    ),
                    "context": f"...{context_window}...",
                }
            )
        return findings

    def graph_based_analysis(self, data):
        potential_pii = []
        sentences = data.split(". ")
        for sentence in sentences:
            email_matches = re.findall(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", sentence
            )
            phone_matches = re.findall(
                r"\b(?:\+?1[\s.-]?)?(\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b",
                sentence,
            )
            ssn_matches = re.findall(r"\b\d{3}-\d{2}-\d{4}\b", sentence)
            name_matches = []
            doc = nlp(sentence)
            for token in doc.ents:
                if token.label_ in ["PERSON"]:
                    name_matches.append(token.text)
            if email_matches or phone_matches or ssn_matches or name_matches:
                record = {}
                if email_matches:
                    record["email"] = email_matches[0]
                if phone_matches:
                    record["phone"] = phone_matches[0]
                if ssn_matches:
                    record["ssn"] = ssn_matches[0]
                if name_matches:
                    record["name"] = name_matches[0]
                potential_pii.append(record)
        G = nx.Graph()
        for record in potential_pii:
            nodes = [str(v) for v in record.values()]
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    G.add_edge(nodes[i], nodes[j])
        clusters = list(nx.connected_components(G))
        return G, clusters, potential_pii

    def deduplicate_findings(self, findings, line_num, category):
        unique_findings = []
        for finding in findings:
            pii_value = finding["value"]
            if pii_value not in self.UNIQUE_PII:
                self.UNIQUE_PII.add(pii_value)
                unique_findings.append(finding)
                self.PII_OUTPUT[line_num].append(pii_value)
                self.PII_DETAILS[line_num].append(
                    {
                        "value": pii_value,
                        "category": category,
                        "method": finding.get("method", "unknown"),
                        "confidence": finding.get("confidence", "unknown"),
                        "reason": finding.get("reason", ""),
                    }
                )
                self.PII_PATTERN[category] += 1
            elif self.debug:
                print(
                    f"Duplicate PII detected and skipped: {pii_value} (Category: {category})"
                )
        return unique_findings

    def keyword_detection(self, data):
        rows = data.split(". ")
        for row, sentence in enumerate(rows):
            doc = nlp(sentence)
            for token in doc.ents:
                if token.label_ in ["PERSON", "ORG", "GPE", "DATE"]:
                    if token.label_ not in self.PII_KEYWORD:
                        self.PII_KEYWORD[token.label_] = []
                finding = {
                    "value": token.text,
                    "method": "keyword_detection",
                    "confidence": "Medium",
                    "reason": f"Detected by NER as {token.label_}",
                }
                if token.label_ in ["DATE"]:
                    self.deduplicate_findings([finding], row, "Dates")
                elif token.label_ in ["PERSON"]:
                    self.deduplicate_findings([finding], row, "Names")
                elif token.label_ in ["GPE"]:
                    self.deduplicate_findings([finding], row, "Addresses")
                elif token.label_ in ["ORG"]:
                    self.deduplicate_findings([finding], row, "Sensitive_Words")

    def pattern_detection(self, data):
        patterns = {
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PHONE": r"\b(?:\+?1[\s.-]?)?(\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b",
            "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "Credit_Card": r"\b\d{4}-\d{4}-\d{4}-\d{4}\b|\b\d{16}\b",
            "Expiration_Date": r"\b\d{2}/\d{2}\b",
            "CVV": r"(?i)(cvv|cvc|cid|security\s+code)[\s:]*['\"]?\d{3,4}['\"]?",
            "Driver's_License": r"(?i)\b(?:[A-Z]{1,3}\d{4,8}|[A-Z]\d{6,12}|\d{3}[A-Z]{2}\d{4})\b",
            "Addresses": r"(\d{1,5}\s\w+\s\w+)|(P\.O\.\sBox\s\d+)|(\d{5})",
            "IPv4_Address": r"\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}\b",
            "IPV6_Address": r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|:(:[0-9a-fA-F]{1,4}){1,7}|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|::((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|(::ffff|::)ffff:([0-9]{1,3}\.){3}[0-9]{1,3}",
        }
        rows = data.split(". ") if isinstance(data, str) else data
        for row, text in enumerate(rows):
            for category, pattern in patterns.items():
                matches = re.finditer(pattern, text)
                for match in matches:
                    finding = {
                        "value": match.group(),
                        "method": "pattern_detection",
                        "confidence": "Medium",
                        "reason": f"Detected by regex pattern for {category}",
                    }
                    self.deduplicate_findings([finding], row, category)

    def proximity_detection(self, data):
        if not self.enable_proximity:
            return
        patterns = {
            "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PHONE": r"\b(?:\+?1[\s.-]?)?(\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b",
            "Credit_Card": r"\b\d{4}-\d{4}-\d{4}-\d{4}\b|\b\d{16}\b",
            "CVV": r"(?i)(cvv|cvc|cid|security\s+code)[\s:]*['\"]?\d{3,4}['\"]?",
            "Driver's_License": r"(?i)\b(?:[A-Z]{1,3}\d{4,8}|[A-Z]\d{6,12}|\d{3}[A-Z]{2}\d{4})\b",
        }
        rows = data.split(". ")
        for row, text in enumerate(rows):
            for category, pattern in patterns.items():
                if category in self.proximity_keywords:
                    findings = self.proximity_analysis(
                        text,
                        pattern,
                        self.proximity_keywords[category],
                        category,
                    )
                    if findings:
                        self.deduplicate_findings(findings, row, category)

    def graph_detection(self, data):
        if not self.enable_graph:
            return
        try:
            G, clusters, potential_pii = self.graph_based_analysis(data)
            rows = data.split(". ")
            for row, text in enumerate(rows):
                for cluster in clusters:
                    cluster_items = list(cluster)
                    if len(cluster_items) > 1:
                        for item in cluster_items:
                            if item in text:
                                finding = {
                                    "value": item,
                                    "method": "graph_analysis",
                                    "confidence": "High",
                                    "reason": f"Found in cluster with {len(cluster_items)-1} other PII items",
                                }
                                category = self._categorize_pii_item(item)
                                if category:
                                    self.deduplicate_findings(
                                        [finding], row, category
                                    )
        except Exception as e:
            if self.debug:
                print(f"Graph analysis error: {e}")

    def _categorize_pii_item(self, item):
        if re.match(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", item
        ):
            return "EMAIL"
        elif re.match(
            r"\b(?:\+?1[\s.-]?)?(\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b", item
        ):
            return "PHONE"
        elif re.match(r"\b\d{3}-\d{2}-\d{4}\b", item):
            return "SSN"
        elif re.match(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b|\b\d{16}\b", item):
            return "Credit_Card"
        elif re.match(
            r"\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}\b",
            item,
        ):
            return "IPv4_Address"
        return None

    def detect_pii(self, data):
        doc = data
        threads = []
        keyword_thread = threading.Thread(
            target=self.keyword_detection, args=(doc,)
        )
        pattern_thread = threading.Thread(
            target=self.pattern_detection, args=(doc,)
        )
        threads.extend([keyword_thread, pattern_thread])
        if self.enable_proximity:
            proximity_thread = threading.Thread(
                target=self.proximity_detection, args=(doc,)
            )
            threads.append(proximity_thread)
        if self.enable_graph:
            graph_thread = threading.Thread(
                target=self.graph_detection, args=(doc,)
            )
            threads.append(graph_thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def output_function(self, data):
        self.detect_pii(data)
        if self.output and self.debug:
            print(json.dumps(self.get_detection_summary(), indent=2))
        if max(self.PII_PATTERN.values()) > 0:
            if self.log_type == "Block":
                print("PII Detected - Entry is Not Loggable")
            elif self.log_type == "Mask":
                print("PII Detected - Entry is Redacted")
            elif self.log_type == "Log":
                print("PII Detected - Message Logged Anyways")
        else:
            print("No PII Detected - Entry is Safe to Log")

    def get_detection_summary(self):
        summary = {
            "total_detections": sum(self.PII_PATTERN.values()),
            "categories": self.PII_PATTERN.copy(),
            "unique_pii_count": len(self.UNIQUE_PII),
            "detailed_findings": self.PII_DETAILS,
        }
        return summary


def read_text_from_path(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input path not found: {path}")
    if os.path.isdir(path):
        raise IsADirectoryError(
            f"Expected a file, received a directory: {path}"
        )
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced PII detection on text/log files."
    )
    parser.add_argument("path", help="Path to input text/log file")
    parser.add_argument(
        "--output-json",
        dest="output_json",
        help="Optional path to write detection JSON summary",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Redact detected PII in memory (not written back)",
    )
    parser.add_argument(
        "--log-type",
        choices=["Block", "Mask", "Log"],
        default="Block",
        help="Logging behavior when PII is detected",
    )
    parser.add_argument(
        "--no-proximity", action="store_true", help="Disable proximity analysis"
    )
    parser.add_argument(
        "--no-graph", action="store_true", help="Disable graph analysis"
    )
    parser.add_argument(
        "--window",
        type=int,
        default=50,
        help="Window size for proximity analysis",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable verbose debug output"
    )

    args = parser.parse_args()

    text = read_text_from_path(args.path)

    detector = Enhanced_PII_Logging(
        text,
        output=True,
        replace=args.replace,
        log_type=args.log_type,
        debug=args.debug,
        enable_proximity=not args.no_proximity,
        enable_graph=not args.no_graph,
        window_size=args.window,
    )

    summary = detector.get_detection_summary()
    if args.output_json:
        try:
            with open(args.output_json, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            print(f"Wrote detection summary to {args.output_json}")
        except Exception as e:
            print(f"Failed to write JSON summary: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
