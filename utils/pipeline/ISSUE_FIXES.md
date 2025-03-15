# Document Processing Pipeline Issue Fixes

This document outlines specific issues identified in the document processing pipeline and proposes detailed fixes for each one.

## 1. Classification Override Issue

### Problem Description
HVAC specification documents with multiple tables are being classified as "FORM" instead of "HVAC_SPECIFICATION". This occurs because the generic classification rule in `rule_based.py` classifies any document with more than 3 tables as a "FORM" with a confidence of 0.6, which may override the specific HVAC classification rules.

### Code Analysis
In `utils/pipeline/processors/classifiers/rule_based.py`, the `_classify_generic` method is called when no specific document type matches with sufficient confidence. This method contains the following logic:

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

### Proposed Fixes

#### Option 1: Modify Rule-Based Classifier to Prioritize Specific Rules

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
        # If no specific type matched, try to determine a generic type
        return self._classify_generic(document_data, features)

    return {
        "document_type": best_match[0],
        "confidence": best_match[1],
        "schema_pattern": best_match[2],
        "key_features": best_match[3],
    }
```

#### Option 2: Increase Confidence Threshold for HVAC Documents in Configuration

In `utils/pipeline/config/hvac_config.json`, increase the confidence threshold for HVAC documents:

```json
"HVAC_SPECIFICATION": {
  "title_keywords": [
    "hvac",
    "heating",
    "ventilation",
    "air conditioning",
    "mechanical",
    "air handling",
    "ductwork",
    "refrigeration",
    "cooling",
    "thermal"
  ],
  "content_keywords": [
    "temperature",
    "humidity",
    "airflow",
    "ductwork",
    "refrigerant",
    "cooling",
    "heating",
    "ventilation",
    "air handling unit",
    "ahu",
    "vav",
    "chiller",
    "boiler",
    "condenser",
    "evaporator",
    "thermostat",
    "diffuser",
    "damper",
    "plenum",
    "insulation",
    "filter",
    "air quality",
    "ashrae"
  ],
  "patterns": [
    "°f",
    "°c",
    "cfm",
    "btu",
    "btuh",
    "ton",
    "kw",
    "hp",
    "psi",
    "inWC",
    "inH2O",
    "fpm",
    "rpm",
    "db",
    "wb",
    "rh%",
    "merv"
  ],
  "weights": {
    "title_match": 0.4,
    "content_match": 0.4,
    "pattern_match": 0.2
  },
  "threshold": 0.3,  // Change to 0.7 to ensure it overrides the generic FORM classification
  "schema_pattern": "hvac_specification"
}
```

#### Option 3: Add Special Case for HVAC Documents with Tables

Add a special case in the `_classify_generic` method to check for HVAC-specific features even when there are multiple tables:

```python
def _classify_generic(self, document_data: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify document into generic categories when specific types don't match.
    """
    # Check for HVAC documents with tables
    content = " ".join([section.get("content", "") for section in document_data.get("content", [])])
    hvac_keywords = ["hvac", "heating", "ventilation", "air conditioning", "temperature", "humidity", "airflow"]
    hvac_keyword_count = sum(1 for keyword in hvac_keywords if keyword.lower() in content.lower())
    
    if hvac_keyword_count >= 3 and features.get("table_count", 0) > 3:
        return {
            "document_type": "HVAC_SPECIFICATION",
            "confidence": 0.65,  # Slightly higher than FORM confidence
            "schema_pattern": "hvac_specification",
            "key_features": ["hvac_keywords", "multiple_tables"],
        }
    
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

### Recommended Approach

Option 1 is the most robust solution as it addresses the fundamental issue of prioritization in the classification logic. It ensures that specific document types with reasonable confidence are always preferred over generic types, regardless of the number of tables or other generic features.

## 2. Table Detection Limitations

### Problem Description
Complex tables in PDF documents may not be detected correctly, leading to incomplete or incorrect table structure information.

### Code Analysis
In `utils/pipeline/processors/pdf_extractor.py`, the `_extract_tables` method uses two approaches for table detection:
1. Layout analysis using PyMuPDF's block structure
2. Text-based table detection as a fallback

Both approaches have limitations with complex tables, especially those with merged cells, irregular structures, or tables that span multiple pages.

### Proposed Fix
Enhance the table detection algorithm with a more sophisticated approach that combines layout analysis with text pattern recognition:

```python
def _extract_tables(self, doc) -> List[Dict[str, Any]]:
    """
    Extract tables from the PDF document with improved structure detection.
    """
    tables = []
    
    try:
        # Use PyMuPDF's improved table detection
        for page_num, page in enumerate(doc):
            # First try to detect tables using layout analysis
            try:
                # Get blocks that might be tables
                blocks = page.get_text("dict")["blocks"]
                
                # Identify potential table blocks based on multiple criteria
                for block in blocks:
                    # Check if block has multiple lines (potential table)
                    if "lines" in block and len(block["lines"]) > 2:
                        # Additional checks for table-like structure
                        is_table = self._is_likely_table(block)
                        
                        if is_table:
                            table_data, headers, column_count = self._extract_table_data(block)
                            
                            # Only add if we have actual data
                            if table_data:
                                # Add table with structure
                                tables.append({
                                    "page": page_num + 1,
                                    "table_number": len(tables) + 1,
                                    "headers": headers,
                                    "data": table_data,
                                    "column_count": column_count,
                                    "row_count": len(table_data),
                                    "detection_method": "layout_analysis",
                                })
            except Exception as layout_error:
                self.logger.warning(f"Layout analysis failed: {str(layout_error)}")
            
            # Try advanced text-based table detection if no tables found
            if not any(table["page"] == page_num + 1 for table in tables):
                text_tables = self._detect_tables_from_text(page)
                tables.extend(text_tables)
                
    except Exception as e:
        self.logger.warning(f"Error during table extraction: {str(e)}")
    
    return tables

def _is_likely_table(self, block):
    """
    Determine if a block is likely to be a table based on structure.
    """
    if "lines" not in block or len(block["lines"]) < 3:
        return False
    
    # Check for consistent number of spans across lines
    span_counts = [len(line.get("spans", [])) for line in block["lines"]]
    if len(set(span_counts)) <= 1:  # All lines have same number of spans
        return False  # Probably just regular text
    
    # Check for alignment patterns
    x_positions = []
    for line in block["lines"]:
        for span in line.get("spans", []):
            x_positions.append(span["origin"][0])
    
    # Count unique x-positions (potential column starts)
    unique_x = set(round(x, 1) for x in x_positions)
    if len(unique_x) >= 3:  # At least 3 distinct column positions
        return True
    
    return False

def _extract_table_data(self, block):
    """
    Extract structured data from a table block.
    """
    table_data = []
    headers = []
    
    # Identify potential column positions
    x_positions = []
    for line in block["lines"]:
        for span in line.get("spans", []):
            x_positions.append(span["origin"][0])
    
    # Group x-positions to identify column boundaries
    x_clusters = self._cluster_positions(x_positions)
    
    # Process rows
    for row_idx, line in enumerate(block["lines"]):
        if "spans" not in line:
            continue
        
        # Map spans to columns based on x-position
        row_data = [""] * len(x_clusters)
        for span in line["spans"]:
            col_idx = self._get_column_index(span["origin"][0], x_clusters)
            if col_idx >= 0:
                row_data[col_idx] += span["text"] + " "
        
        # Clean up row data
        row_data = [cell.strip() for cell in row_data]
        
        # First row might be headers
        if row_idx == 0 and any(cell.isupper() for cell in row_data if cell):
            headers = row_data
        else:
            # Only add non-empty rows
            if any(cell for cell in row_data):
                table_data.append(row_data)
    
    # Determine column count
    column_count = len(headers) if headers else (max(len(row) for row in table_data) if table_data else 0)
    
    return table_data, headers, column_count

def _cluster_positions(self, positions, threshold=10):
    """
    Cluster x-positions to identify column boundaries.
    """
    if not positions:
        return []
    
    # Sort positions
    sorted_pos = sorted(positions)
    
    # Initialize clusters
    clusters = [[sorted_pos[0]]]
    
    # Cluster positions
    for pos in sorted_pos[1:]:
        if pos - clusters[-1][-1] <= threshold:
            # Add to existing cluster
            clusters[-1].append(pos)
        else:
            # Start new cluster
            clusters.append([pos])
    
    # Get average position for each cluster
    return [sum(cluster) / len(cluster) for cluster in clusters]

def _get_column_index(self, x_position, column_positions):
    """
    Determine which column a span belongs to based on its x-position.
    """
    for i, pos in enumerate(column_positions):
        if abs(x_position - pos) <= 20:  # Threshold for matching
            return i
    return -1

def _detect_tables_from_text(self, page):
    """
    Detect tables using text patterns.
    """
    tables = []
    text = page.get_text("text")
    
    # Look for common table indicators
    if any(pattern in text for pattern in ["TABLE", "Table", "|", "+"]):
        # Implementation of advanced text-based table detection
        # ...
    
    return tables
```

This enhanced implementation would:
1. Use more sophisticated criteria to identify tables
2. Better handle column alignment and structure
3. Cluster x-positions to identify column boundaries
4. Provide more accurate header detection

## 3. Content Truncation Fix

### Problem Description
Previous implementation limited section content to 100 characters, resulting in truncated content in the output.

### Code Analysis
In `utils/pipeline/processors/pdf_extractor.py`, the `_extract_sections` method was truncating content:

```python
# Add to current section content WITH truncation
current_section["content"] += line[:100] + "\n"
```

### Fix Implementation
The fix has already been implemented by removing the truncation:

```python
# Add to current section content WITHOUT truncation
current_section["content"] += line + "\n"
```

This change ensures that the full content of each section is captured in the output.

## 4. Schema Storage Enhancement

### Problem Description
The schema storage did not include actual content samples and table data, limiting the usefulness of the schema for analysis and visualization.

### Code Analysis
In `utils/pipeline/schema/registry.py`, the `record` method was not storing content samples and table data.

### Proposed Fix
Enhance the `record` method to store content samples and table data:

```python
def record(self, document_data: Dict[str, Any], document_type: str, document_name: Optional[str] = None) -> str:
    """
    Record a document schema in the registry.
    
    Args:
        document_data: Document data to record
        document_type: Type of the document
        document_name: Optional name of the document
        
    Returns:
        Schema ID
    """
    # Generate schema ID
    schema_id = f"{document_type.lower()}_{int(time.time())}"
    
    # Extract metadata
    metadata = document_data.get("metadata", {})
    
    # Extract content samples (up to 5 sections)
    content_samples = []
    for section in document_data.get("content", [])[:5]:
        # Store title and a sample of the content
        content_sample = {
            "title": section.get("title", ""),
            "content_sample": section.get("content", "")[:200] + "..." if len(section.get("content", "")) > 200 else section.get("content", ""),
            "content_length": len(section.get("content", "")),
        }
        content_samples.append(content_sample)
    
    # Extract table data (up to 3 tables)
    table_samples = []
    for table in document_data.get("tables", [])[:3]:
        # Store table structure and sample data
        table_sample = {
            "headers": table.get("headers", []),
            "column_count": table.get("column_count", 0),
            "row_count": table.get("row_count", 0),
            "data_sample": table.get("data", [])[:3],  # First 3 rows
        }
        table_samples.append(table_sample)
    
    # Create schema record
    schema = {
        "id": schema_id,
        "document_type": document_type,
        "document_name": document_name,
        "recorded_at": datetime.now().isoformat(),
        "metadata": metadata,
        "content_samples": content_samples,
        "table_samples": table_samples,
        "section_count": len(document_data.get("content", [])),
        "table_count": len(document_data.get("tables", [])),
    }
    
    # Save schema to registry
    self._save_schema(schema_id, schema)
    
    return schema_id
```

This enhancement ensures that the schema includes:
1. Content samples from the document
2. Table structure information including headers
3. Sample table data for visualization
4. Accurate counts of sections and tables

These enhancements will make the schema more useful for analysis and visualization, and will support the improved visualization tools.
