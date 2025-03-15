# Document Processing Pipeline Issue Fixes

This document outlines specific issues identified in the document processing pipeline and proposes detailed fixes for each one.

## 1. Classification Override Issue (✅ FIXED)

### Problem Description
HVAC specification documents with multiple tables were being classified as "FORM" instead of "HVAC_SPECIFICATION". This occurred because the generic classification rule in `rule_based.py` classified any document with more than 3 tables as a "FORM" with a confidence of 0.6, which overrode the specific HVAC classification rules.

### Code Analysis
In `utils/pipeline/processors/classifiers/rule_based.py`, the `_classify_generic` method was called when no specific document type matched with sufficient confidence. This method contained the following logic:

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

### Implemented Fixes

We implemented a combination of fixes to address this issue:

1. **Modified Pipeline Class to Pass Entire Configuration**:
   ```python
   # In utils/pipeline/pipeline.py
   def _classify_document(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
       # Get classifier configuration
       classifier_config = self.config.get("classification", {})
       classifier_type = classifier_config.get("method", "rule_based")

       # Import the document classifier
       from utils.pipeline.processors.document_classifier import DocumentClassifier

       # Pass the entire config to the classifier, not just the classification section
       classifier = DocumentClassifier(classifier_type, self.config)

       # Perform classification
       classification = classifier.classify(validated_data)
       return classification
   ```

2. **Enhanced Rule-Based Classifier to Check Document Metadata**:
   ```python
   # In utils/pipeline/processors/classifiers/rule_based.py
   def _get_best_match(self, document_data: Dict[str, Any], features: Dict[str, Any]) -> Tuple[str, float, str, List[str]]:
       # Check metadata for keywords
       metadata = document_data.get("metadata", {})
       metadata_text = " ".join([str(v).lower() for v in metadata.values()])
       
       # Check title keywords in metadata
       title_keywords = rule.get("title_keywords", [])
       if title_keywords:
           metadata_matches = sum(1 for keyword in title_keywords if keyword.lower() in metadata_text)
           if metadata_matches > 0:
               title_weight = rule.get("weights", {}).get("title_match", 0.4)
               metadata_confidence = title_weight * (metadata_matches / len(title_keywords))
               confidence += metadata_confidence
               key_features.append("metadata_match")
   ```

3. **Improved Filename Pattern Matching**:
   ```python
   # In utils/pipeline/processors/classifiers/rule_based.py
   def classify(self, document_data: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
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
   ```

4. **Modified Generic Classification Threshold**:
   ```python
   # In utils/pipeline/processors/classifiers/rule_based.py
   # Only use generic classification if confidence is very low
   if best_match[0] == "UNKNOWN" or best_match[1] < 0.2:  # Lower threshold for falling back to generic
       # If no specific type matched or confidence is very low, try to determine a generic type
       return self._classify_generic(document_data, features)
   ```

### Verification
The fix has been verified by running the pipeline with the HVAC configuration:
```bash
python -m utils.pipeline.run_pipeline --file "utils/pipeline/data/input/MF-SPECS_232500 FL - HVAC WATER TREATMENT.pdf" --output utils/pipeline/data/output --config utils/pipeline/config/hvac_config.json
```

The document is now correctly classified as "HVAC_SPECIFICATION" with confidence 0.8, and the classification information is included in the output JSON file.

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

## 4. Schema Storage Enhancement (✅ COMPLETED)

### Problem Description
The schema storage did not include actual content samples and table data, limiting the usefulness of the schema for analysis and visualization.

### Code Analysis
In `utils/pipeline/schema/registry.py`, the `record` method was not storing content samples and table data.

### Fix Implementation
The `record` method in `utils/pipeline/schema/registry.py` has been enhanced to store content samples and table data:

```python
def record(self, document_data: Dict[str, Any], document_type: str, document_name: Optional[str] = None) -> str:
    """
    Record a document schema in the registry with enhanced data storage.

    Args:
        document_data: Document data to record
        document_type: Type of the document
        document_name: Name of the document (optional)

    Returns:
        Schema ID if successful, empty string otherwise
    """
    try:
        # Generate schema ID
        schema_id = self._generate_schema_id(document_type)

        # Extract metadata
        metadata = document_data.get("metadata", {})

        # Extract content samples (up to 5 sections)
        content_samples = []
        for section in document_data.get("content", [])[:5]:
            # Store title and full content (no truncation)
            content_sample = {
                "title": section.get("title", ""),
                "content": section.get("content", ""),
                "level": section.get("level", 0),
                "has_children": bool(section.get("children")),
                "child_count": len(section.get("children", [])),
            }
            content_samples.append(content_sample)

        # Extract table data samples (up to 3 tables)
        table_samples = []
        for table in document_data.get("tables", [])[:3]:
            # Store table structure and sample data
            table_sample = {
                "headers": table.get("headers", []),
                "column_count": table.get("column_count", 0),
                "row_count": table.get("row_count", 0),
                "data_sample": table.get("data", [])[:5],  # First 5 rows
                "detection_method": table.get("detection_method", "unknown"),
                "page": table.get("page", 0),
                "border_info": table.get("border_info", {}),
            }
            table_samples.append(table_sample)

        # Create enhanced schema record
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
            "document_path": document_data.get("path", ""),
        }

        # Save schema to registry
        self._save_schema(schema_id, schema)

        # Update in-memory schemas
        self.schemas[schema_id] = schema

        self.logger.info(
            f"Recorded enhanced schema {schema_id} for document type {document_type}"
        )
        return schema_id

    except Exception as e:
        self.logger.error(f"Error recording schema: {str(e)}", exc_info=True)
        return ""
```

This enhancement ensures that the schema includes:
1. Content samples from the document without truncation
2. Table structure information including headers, column counts, and row counts
3. Sample table data for visualization (up to 5 rows per table)
4. Detection method information for tables
5. Border information for visualization
6. Accurate counts of sections and tables

These enhancements make the schema more useful for analysis and visualization, and support the improved visualization tools. The implementation has been tested and verified to work correctly.

## 5. Enhanced Markdown Formatter (✅ COMPLETED)

### Problem Description
The standard markdown formatter produced basic markdown output that lacked structure, proper formatting, and advanced features. This resulted in poor readability and limited usefulness of the markdown output.

### Code Analysis
The original markdown formatter in `utils/pipeline/processors/formatters/markdown_formatter.py` had several limitations:

1. No support for content segmentation (paragraphs, lists, code blocks)
2. No inline formatting for emphasis, bold, etc.
3. Poor handling of tables, especially complex ones with merged cells
4. No support for special elements like notes, warnings, and definitions
5. No post-processing for improved readability
6. No validation of the generated markdown

### Fix Implementation
We implemented an enhanced markdown formatter in `utils/pipeline/processors/formatters/enhanced_markdown_formatter.py` that extends the base markdown formatter with advanced features:

```python
class EnhancedMarkdownFormatter(MarkdownFormatter):
    """
    Enhanced formatter for converting extracted PDF content into readable Markdown.

    Features:
    - Content segmentation (paragraphs, lists, code blocks, etc.)
    - Enhanced table formatting with support for complex tables
    - Inline formatting detection
    - Special element handling (notes, warnings, definitions, etc.)
    - Post-processing for improved readability
    - Markdown validation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced markdown formatter.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__()
        self.config = config or {}
        self.logger = get_logger(__name__)

    def format(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analyzed data into a Markdown structure with enhanced features.

        Args:
            analyzed_data: Data from the PDF analyzer

        Returns:
            Formatted data structure with Markdown content
        """
        self.logger.info("Formatting PDF content as Markdown with enhanced features")

        # Implementation details...
```

Key enhancements include:

1. **Content Segmentation**: Automatically identifies and formats paragraphs, lists, code blocks, and other structural elements
2. **Inline Formatting**: Detects and applies appropriate formatting for emphasis, bold, code, etc.
3. **Enhanced Table Handling**: Supports complex tables with merged cells using HTML when needed
4. **Special Element Handling**: Properly formats notes, warnings, definitions, and figure captions
5. **Post-Processing**: Improves readability with consistent spacing and formatting
6. **Validation**: Validates the generated markdown and provides statistics

### Configuration
The enhanced markdown formatter can be enabled by setting `use_enhanced_markdown: true` in the pipeline configuration:

```json
{
  "output_format": "MARKDOWN",
  "use_enhanced_markdown": true,
  "markdown_options": {
    "content_segmentation": true,
    "inline_formatting": true,
    "enhanced_tables": true,
    "html_for_complex_tables": true,
    "html_anchors": true,
    "post_processing": true,
    "validation": true,
    "include_validation_report": false
  }
}
```

### Integration
We updated the pipeline to properly pass the configuration to the formatter factory:

1. Modified `FileProcessor._extract_pipeline_config()` to include markdown-related configuration
2. Updated `Pipeline._get_output_format()` to check for enhanced markdown setting
3. Enhanced `Pipeline._format_output()` to pass markdown configuration to the formatter

### Verification
The enhanced markdown formatter has been tested with various documents and produces significantly improved output:

- Better structure with proper headings, paragraphs, and lists
- Improved readability with consistent formatting
- Better handling of tables, including complex ones
- Support for special elements like notes and warnings
- HTML anchors for cross-references

Example output shows:
- HTML anchors for section headings: `<a id="section-id"></a>`
- Bold formatting for terms in all caps: `**AIA**`, `**HVAC**`, etc.
- Proper heading structure with appropriate levels
- Validation report at the end of the file
