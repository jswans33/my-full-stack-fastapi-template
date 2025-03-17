# Configuration Files Reference

This document provides a reference for all configuration files in the pipeline.

## Core Configuration Files

| File | Format | Purpose | Status |
|------|--------|---------|--------|
| **reference_config.yaml** | YAML | Complete reference example of pipeline configuration | Reference Template |
| **hvac_config.yaml** | YAML | HVAC-specific pipeline configuration | Active |

## Classifier Configuration Files

| File | Format | Purpose | Status |
|------|--------|---------|--------|
| **reference_classifier_config.yaml** | YAML | Reference classifier configuration | Reference Template |
| **hvac_classifier_config.yaml** | YAML | HVAC-specific classifier configuration | Active |

## Output Format Configuration Files

| File | Format | Purpose | Status |
|------|--------|---------|--------|
| **enhanced_markdown_config.json** | JSON | Enhanced markdown configuration | Active |

## System Configuration Files

| File | Format | Purpose | Status |
|------|--------|---------|--------|
| **schema_registry.yaml** | YAML | Schema registry configuration | Active |

## File Relationships

- **reference_config.yaml** → **hvac_config.yaml**: hvac_config.yaml is a specialized implementation of reference_config.yaml
- **reference_classifier_config.yaml** → **hvac_classifier_config.yaml**: hvac_classifier_config.yaml extends reference_classifier_config.yaml with HVAC-specific rules

## Usage in Examples

| Example | Configuration Files Used |
|---------|--------------------------|
| document_classification_example.py | reference_classifier_config.yaml |
| debug_hvac_classifier.py | hvac_classifier_config.yaml |
| test_hvac_classification.py | hvac_classifier_config.yaml, hvac_config.yaml |
| test_sample_pdf.py | reference_config.yaml, reference_classifier_config.yaml |

## Configuration Guidelines

1. **Reference Templates**
   - Files prefixed with `reference_` serve as templates and documentation
   - Do not modify these files for specific implementations
   - Use them as a base for creating specialized configurations

2. **Active Configurations**
   - Files without the `reference_` prefix are active configurations
   - These can be customized for specific use cases
   - Follow the structure shown in reference files

3. **Version Control**
   - Configuration versions are tracked within the files themselves
   - Use the `version` field in configurations when available
   - Avoid version numbers in filenames

4. **Format Standards**
   - YAML is preferred for human-readable configurations
   - JSON is used only when required by specific components
   - Maintain consistent formatting within each file type
