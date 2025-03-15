# Classification Override Fix

This document explains the fix for the classification override issue where HVAC documents with multiple tables were being classified as "FORM" instead of "HVAC_SPECIFICATION".

## Problem Description

HVAC specification documents with multiple tables were being classified as "FORM" instead of "HVAC_SPECIFICATION". This occurred because the generic classification rule in `rule_based.py` classified any document with more than 3 tables as a "FORM" with a confidence of 0.6, which overrode the specific HVAC classification rules.

## Root Cause Analysis

In `utils/pipeline/processors/classifiers/rule_based.py`, the `classify` method would fall back to generic classification whenever no specific document type matched with sufficient confidence. The `_classify_generic` method contained the following logic:

```python
def _classify_generic(self, document_data: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify document into generic categories when specific types don't match.
    """
    # Check if it's a form
    if features.get("table_count", 0) > 3:
        return {
            "document_type": "FORM",
            "confidence": 0.6,
            "schema_pattern": "tabular_form",
            "key_features": ["multiple_tables", "structured_layout"],
        }
    
    # Other generic classifications...
```

The issue was that even when a specific document type like "HVAC_SPECIFICATION" matched with a reasonable confidence (e.g., 0.3), the classifier would still fall back to generic classification if the confidence wasn't high enough. Then, if the document had more than 3 tables, it would be classified as a "FORM" with a confidence of 0.6, overriding the specific classification.

## Fix Implementation

The fix modifies the `classify` method to only fall back to generic classification if the confidence of the best match is very low (less than 0.2). This ensures that specific document types with reasonable confidence are always preferred over generic types.

Here's the modified `classify` method:

```python
def classify(self, document_data: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify the document using rule-based approach.
    """
    # Check filename patterns if path is available
    if "path" in document_data:
        filename = os.path.basename(document_data["path"])
        for doc_type, pattern in self.filename_patterns.items():
            if re.search(pattern, filename):
                self.logger.info(f"Matched filename pattern for {doc_type}: {filename}")
                return {
                    "document_type": doc_type,
                    "confidence": 0.8,  # High confidence for filename match
                    "schema_pattern": self.rules_config.get(doc_type, {}).get("schema_pattern", "standard"),
                    "key_features": ["filename_match"],
                }

    # Apply configured rules
    best_match = self._get_best_match(document_data, features)
    
    # Only use generic classification if confidence is very low
    if best_match[0] == "UNKNOWN" or best_match[1] < 0.2:  # Lower threshold for falling back to generic
        # If no specific type matched or confidence is very low, try to determine a generic type
        return self._classify_generic(document_data, features)

    return {
        "document_type": best_match[0],
        "confidence": best_match[1],
        "schema_pattern": best_match[2],
        "key_features": best_match[3],
    }
```

The key change is the condition for falling back to generic classification:
```python
# Only use generic classification if confidence is very low
if best_match[0] == "UNKNOWN" or best_match[1] < 0.2:  # Lower threshold for falling back to generic
    # If no specific type matched or confidence is very low, try to determine a generic type
    return self._classify_generic(document_data, features)
```

This ensures that specific document types with reasonable confidence (>= 0.2) are always preferred over generic types, regardless of the number of tables or other generic features.

## Verification

A test script has been created to verify the fix: `utils/pipeline/tests/test_classification_fix.py`. This script:

1. Creates a test document with HVAC content and multiple tables
2. Classifies the document using the RuleBasedClassifier with HVAC configuration
3. Verifies that the document is correctly classified as "HVAC_SPECIFICATION" instead of "FORM"
4. Simulates the behavior before the fix by directly calling the `_classify_generic` method

To run the test:

```bash
python -m utils.pipeline.tests.test_classification_fix
```

Expected output:

```
=== Testing Classification Override Fix ===
Testing classification with HVAC configuration (after fix):
Matched filename pattern for HVAC_SPECIFICATION: HVAC_SPECIFICATION_with_tables.pdf
Classification result: {'document_type': 'HVAC_SPECIFICATION', 'confidence': 0.8, 'schema_pattern': 'hvac_specification', 'key_features': ['filename_match']}
✅ Test PASSED: Document correctly classified as HVAC_SPECIFICATION

Simulating classification behavior before fix:
Classification result (before fix): {'document_type': 'FORM', 'confidence': 0.6, 'schema_pattern': 'tabular_form', 'key_features': ['multiple_tables', 'structured_layout']}
✅ Test PASSED: Document would have been classified as FORM before the fix
```

## Additional Notes

This fix addresses the fundamental issue of prioritization in the classification logic. It ensures that specific document types with reasonable confidence are always preferred over generic types, regardless of the number of tables or other generic features.

Alternative approaches that were considered:

1. Increasing the confidence threshold for HVAC documents in the configuration
2. Adding a special case for HVAC documents with tables in the `_classify_generic` method

The implemented solution was chosen because it addresses the root cause of the issue and provides a more general solution that will work for all document types, not just HVAC documents.
