# Configuration Files Reference

This document provides a reference for all configuration files in the pipeline.

## Core Configuration Files

| File | Format | Purpose | Status |
|------|--------|---------|--------|
| **example_config.yaml** | YAML | Complete example of pipeline configuration | Reference |
| **hvac_config.yaml** | YAML | HVAC-specific pipeline configuration | Active |
| **hvac_config.json** | JSON | JSON version of hvac_config.yaml | Alternative format (consider removing) |

## Classifier Configuration Files

| File | Format | Purpose | Status |
|------|--------|---------|--------|
| **example_classifier_config.yaml** | YAML | Example classifier configuration | Reference |
| **hvac_classifier_config.yaml** | YAML | HVAC-specific classifier configuration | Active |

## Output Format Configuration Files

| File | Format | Purpose | Status |
|------|--------|---------|--------|
| **enhanced_markdown_config.json** | JSON | Enhanced markdown configuration | Legacy (consider removing) |
| **enhanced_markdown_config_v2.json** | JSON | Updated enhanced markdown configuration | Current |

## System Configuration Files

| File | Format | Purpose | Status |
|------|--------|---------|--------|
| **schema_registry.yaml** | YAML | Schema registry configuration | Active |

## File Relationships

- **example_config.yaml** → **hvac_config.yaml**: hvac_config.yaml is a specialized version of example_config.yaml
- **example_classifier_config.yaml** → **hvac_classifier_config.yaml**: hvac_classifier_config.yaml extends example_classifier_config.yaml with HVAC-specific rules
- **enhanced_markdown_config.json** → **enhanced_markdown_config_v2.json**: v2 is an updated version of the original
- **hvac_config.yaml** ↔ **hvac_config.json**: These contain the same configuration in different formats

## Usage in Examples

| Example | Configuration Files Used |
|---------|--------------------------|
| document_classification_example.py | example_classifier_config.yaml |
| debug_hvac_classifier.py | hvac_classifier_config.yaml |
| test_hvac_classification.py | hvac_classifier_config.yaml, hvac_config.yaml |
| test_sample_pdf.py | example_config.yaml, example_classifier_config.yaml |
