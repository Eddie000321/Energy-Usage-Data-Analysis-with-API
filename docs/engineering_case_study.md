# Energy Pipeline Engineering Case Study

## Problem

The pipeline turns an external monthly API response into analysis-ready CSV data and charts. A successful HTTP request alone is not enough: response-shape drift, mixed customer categories, or a partial rerun could silently change the dataset.

## Decision

The fetch boundary validates the named dataset, API result code, and non-empty rows before retaining only the `개인` category. Monthly responses are stored as deterministic JSON snapshots. Preprocessing reads snapshots in filename order, derives a fixed tabular schema, and overwrites the same output path on a rerun. The pipeline runner stops before preprocessing when collection reports failure.

## Verification

Create an isolated environment and use that same interpreter for dependency installation and verification:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

The network-free suite verifies the request URL and timeout, an exact filtered fetch contract, byte-identical repeated JSON writes, byte-identical repeated CSV generation with a fixed schema and values, ordered pipeline execution, fail-closed stage gating, and API-key redaction in failure output. No live API key or external request is used by these tests. Running the suite with a different Python interpreter that has not installed `requirements.txt` will correctly fail on the required pandas and Matplotlib imports.

## Limits

The fixtures cover representative responses, not every schema variant returned by the live service. Collection requests only rows 1–1000 and has no pagination or retry policy. The configured endpoint uses plain HTTP and puts the API key in the URL path. `total_usage` adds measurements with different physical units, so it is an assignment helper rather than a scientifically normalized energy metric. Chart pixels and the live API contract are not snapshot-tested. Dependency versions are not pinned, so a clean install is isolated but not guaranteed to resolve to the same versions in the future.

## Learning

Separating the network boundary from deterministic transformations makes failures easier to localize and reruns safer. Idempotency is useful evidence: identical raw input produces identical stored JSON and processed CSV instead of accumulating duplicate records or order-dependent output.
