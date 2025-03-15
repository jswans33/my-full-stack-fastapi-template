# Document Processing Pipeline Implementation Plan

This document outlines the specific steps to implement the fixes and enhancements identified in the document processing pipeline.

## Priority 1: Classification Override Fix

### Step 1: Modify Rule-Based Classifier
**File**: `utils/pipeline/processors/classifiers/rule_based.py`
**Change**: Update the `classify` method to prioritize specific document types over generic types

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

### Step 2: Test Classification Fix
1. Run pipeline with HVAC configuration on a document with multiple tables
2. Verify that the document is classified as "HVAC_SPECIFICATION" instead of "FORM"
3. Check confidence level and key features in the classification result

## Priority 2: Table Detection Enhancements

### Step 1: Add Helper Methods for Table Detection
**File**: `utils/pipeline/processors/pdf_extractor.py`
**Change**: Add new helper methods for improved table detection

```python
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
```

### Step 2: Update Extract Tables Method
**File**: `utils/pipeline/processors/pdf_extractor.py`
**Change**: Update the `_extract_tables` method to use the new helper methods

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
            
            # Fallback to text-based table detection
            if not any(table["page"] == page_num + 1 for table in tables):
                text = page.get_text("text")
                
                # Look for common table indicators
                if any(pattern in text for pattern in ["TABLE", "Table", "|", "+"]):
                    # Try to detect table structure from text
                    lines = text.split("\n")
                    table_start = -1
                    table_end = -1
                    
                    # Find table boundaries
                    for i, line in enumerate(lines):
                        if "TABLE" in line.upper() and table_start == -1:
                            table_start = i
                        elif table_start != -1 and not line.strip():
                            # Empty line might indicate end of table
                            if i > table_start + 2:  # At least 2 rows
                                table_end = i
                                break
                    
                    # If we found a table
                    if table_start != -1 and table_end != -1:
                        table_lines = lines[table_start:table_end]
                        
                        # Try to detect headers and data
                        headers = []
                        data = []
                        
                        # First non-empty line after title might be headers
                        for i, line in enumerate(table_lines):
                            if i > 0 and line.strip():  # Skip title
                                # Split by common delimiters
                                cells = re.split(r"\s{2,}|\t|\|", line)
                                cells = [cell.strip() for cell in cells if cell.strip()]
                                
                                if not headers and any(cell.isupper() for cell in cells):
                                    headers = cells
                                else:
                                    data.append(cells)
                        
                        # Add table with structure
                        if data:  # Only add if we have data
                            tables.append({
                                "page": page_num + 1,
                                "table_number": len(tables) + 1,
                                "headers": headers,
                                "data": data,
                                "column_count": len(headers) if headers else (max(len(row) for row in data) if data else 0),
                                "row_count": len(data),
                                "detection_method": "text_analysis",
                            })
    except Exception as e:
        self.logger.warning(f"Error during table extraction: {str(e)}")
    
    return tables
```

### Step 3: Test Table Detection Enhancements
1. Run pipeline on a document with complex tables
2. Verify that tables are correctly detected and structured
3. Check for headers and column information in the output
4. Visualize tables using `visualize_schema tables <schema_id>`

## Priority 3: Schema Storage Enhancements

### Step 1: Update Record Method in Schema Registry
**File**: `utils/pipeline/schema/registry.py`
**Change**: Update the `record` method to store content samples and table data

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

### Step 2: Test Schema Storage Enhancements
1. Run pipeline on a document
2. Check schema registry for content samples and table data
3. Verify that schema includes accurate counts of sections and tables
4. Use visualization tools to confirm data is accessible

## Priority 4: Documentation Updates

### Step 1: Update PIPELINE_USAGE.md
**File**: `utils/pipeline/PIPELINE_USAGE.md`
**Change**: Add examples of using the enhanced configuration system

### Step 2: Update SCHEMA_VISUALIZATION.md
**File**: `utils/pipeline/SCHEMA_VISUALIZATION.md`
**Change**: Update to reflect new visualization capabilities for tables and content

### Step 3: Create Additional Example Configurations
**File**: `utils/pipeline/config/electrical_config.json`
**Change**: Create a new example configuration for electrical specifications

## Testing and Verification

After implementing each fix, follow these verification steps:

1. **Classification Fix Verification**
   - Run pipeline with default configuration and HVAC configuration
   - Compare classification results
   - Verify that HVAC documents with tables are correctly classified

2. **Table Detection Verification**
   - Run pipeline on documents with various table structures
   - Visualize table patterns
   - Check for headers, column counts, and data samples

3. **Schema Storage Verification**
   - Check schema registry for content samples and table data
   - Verify that schema includes accurate counts of sections and tables
   - Use visualization tools to confirm data is accessible

4. **Documentation Verification**
   - Review updated documentation for accuracy and completeness
   - Test examples to ensure they work as described
   - Verify that configuration examples produce expected results

## Implementation Timeline

1. **Day 1**: Implement and test Classification Override Fix
2. **Day 2**: Implement and test Table Detection Enhancements
3. **Day 3**: Implement and test Schema Storage Enhancements
4. **Day 4**: Update documentation and create additional example configurations
5. **Day 5**: Final testing and verification of all enhancements

## Conclusion

This implementation plan provides a clear roadmap for implementing the fixes and enhancements identified in the document processing pipeline. By following this plan, the pipeline will be enhanced to provide more accurate classification, better table detection, and improved schema storage.
