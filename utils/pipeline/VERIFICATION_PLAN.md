# Document Processing Pipeline Verification Plan

This document outlines the plan for verifying the enhancements made to the document processing pipeline, specifically focusing on the classification configuration and data extraction improvements.

## Enhancements to Verify

### 1. Enhanced Data Extraction
- [ ] Complete content extraction (no truncation of section content)
- [ ] Improved table detection with better structure recognition
- [ ] Table headers and column information extraction
- [ ] Enhanced schema storage with content samples and table data

### 2. Configurable Document Classification
- [ ] Central configuration system for document classification
- [ ] Rule-based classifier using configuration instead of hardcoded rules
- [ ] Filename pattern matching for improved classification
- [ ] Configuration examples for different document types

## Testing Methodology

### Step 1: Run Pipeline with Default Configuration
```bash
python -m utils.pipeline.run_pipeline --file "utils/pipeline/data/input/MF-SPECS_232500 FL - HVAC WATER TREATMENT.pdf" --output utils/pipeline/data/output
```
- Expected result: Document likely classified as "FORM" due to generic rule
- Verification: Check classification result in terminal output

### Step 2: Run Pipeline with HVAC Configuration
```bash
python -m utils.pipeline.run_pipeline --file "utils/pipeline/data/input/MF-SPECS_232500 FL - HVAC WATER TREATMENT.pdf" --output utils/pipeline/data/output --config utils/pipeline/config/hvac_config.json
```
- Expected result: Should classify as "HVAC_SPECIFICATION" if configuration is working correctly
- Verification: Check classification result in terminal output

### Step 3: List Schemas to Find Schema IDs
```bash
python -m utils.pipeline.visualize_schema list
```
- Expected result: List of schemas including recently processed documents
- Verification: Note schema IDs for both default and HVAC configuration runs

### Step 4: Verify Table Extraction Enhancements
```bash
python -m utils.pipeline.visualize_schema tables <schema_id>
```
- Expected result: Visualization showing table headers, column counts, and sample data
- Verification: Compare with previous table visualizations to confirm improvements

### Step 5: Verify Content Extraction Enhancements
```bash
python -m utils.pipeline.visualize_schema structure <schema_id>
```
- Expected result: Complete section content without truncation
- Verification: Check for full content in sections

### Step 6: Examine Output JSON Files
```bash
# View the output JSON file
cat utils/pipeline/data/output/MF-SPECS_232500\ FL\ -\ HVAC\ WATER\ TREATMENT.json
```
- Expected result: Complete content, table structures with headers, and proper classification
- Verification: Check for truncation, table structure, and classification information

## Potential Issues and Solutions

### Classification Issues
1. **Issue**: HVAC documents with multiple tables being classified as "FORM"
   - **Root Cause**: Generic rule in `rule_based.py` classifies documents with >3 tables as "FORM" with 0.6 confidence
   - **Solution Options**:
     - Modify `rule_based.py` to prioritize specific document types over generic types
     - Increase confidence threshold for HVAC documents in configuration
     - Add a special case for HVAC documents with tables

### Data Extraction Issues
1. **Issue**: Content truncation
   - **Root Cause**: Previous implementation limited section content to 100 characters
   - **Solution**: Remove content truncation in `pdf_extractor.py`
   - **Verification**: Check for complete content in output

2. **Issue**: Missing table structure information
   - **Root Cause**: Previous implementation didn't capture headers and column information
   - **Solution**: Enhanced table detection in `pdf_extractor.py`
   - **Verification**: Check for headers and column information in output

## Documentation Updates

After verification, the following documentation should be updated:

1. **PIPELINE_USAGE.md**
   - Add examples of using the enhanced configuration system
   - Document new classification options

2. **SCHEMA_VISUALIZATION.md**
   - Update to reflect new visualization capabilities for tables and content

3. **Example Configurations**
   - Create additional example configurations for different document types

## Final Verification Checklist

- [ ] Document classification works correctly with configuration
- [ ] Filename pattern matching improves classification accuracy
- [ ] Section content is complete without truncation
- [ ] Table detection correctly identifies table structures
- [ ] Table headers and column information are captured
- [ ] Schema visualization shows the enhanced data
- [ ] Documentation is updated to reflect all enhancements
