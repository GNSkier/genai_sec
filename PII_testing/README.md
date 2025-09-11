# PII_testing

Repository for testing Personally Identifiable Information (PII) detection methods, including:
- Regex and spaCy NER based detection
- Proximity analysis (context-aware pattern matches)
- Graph-based analysis (clustering related PII)
- Deduplication across methods

## Environment

```bash
conda activate gensec
python -m pip install -q pytest spacy networkx matplotlib
python -m spacy download en_core_web_sm -q
```

## Project layout (key parts)

- `PII_testing/PII_Logging_2.ipynb`: Enhanced detector demo notebook
- `tests/test_pii_logging.py`: Pytests for detector behavior
- `test_data/`: Sample input files (logs, emails) for manual/CLI testing

## Run tests

From the `Homeworks` directory:

```bash
conda activate gensec
pytest -q
```

## Sample data

Use the ready-made inputs under `test_data/`:
- `test_data/log_with_pii.txt`: Contains email, phone, card, CVV, SSN
- `test_data/log_without_pii.txt`: Clean operational logs
- `test_data/email_with_pii.eml`: Names, emails, phone, SSN, address
- `test_data/email_without_pii.eml`: Clean message
- `test_data/mixed_network_and_address.log`: IPv4/IPv6, address, license

## Notebook usage

Open the notebook in this folder to explore the detector with examples:

```bash
jupyter lab PII_testing/PII_Logging_2.ipynb
```

Ensure the `gensec` environment is active so spaCy and its model are available.

