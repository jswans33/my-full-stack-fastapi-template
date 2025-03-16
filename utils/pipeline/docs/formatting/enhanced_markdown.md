# Enhanced Markdown Formatter

The Enhanced Markdown Formatter is an advanced formatter for converting extracted PDF content into readable Markdown with improved structure recognition, table handling, and formatting features.

## Features

- **Content Segmentation**: Automatically identifies and formats paragraphs, lists, code blocks, and blockquotes
- **Enhanced Table Formatting**: Supports complex tables with merged cells using HTML when needed
- **Inline Formatting Detection**: Automatically detects and applies formatting for emphasis, code, and URLs
- **Special Element Handling**: Properly formats notes, warnings, definitions, and figure captions
- **Post-processing**: Improves overall readability with consistent spacing and formatting
- **Markdown Validation**: Validates output and provides warnings for potential issues

## Enabling the Enhanced Markdown Formatter

To use the Enhanced Markdown Formatter, add the following to your pipeline configuration:

```json
{
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

## Configuration Options

The Enhanced Markdown Formatter supports the following configuration options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `content_segmentation` | boolean | `true` | Enable automatic segmentation of content into paragraphs, lists, etc. |
| `inline_formatting` | boolean | `true` | Enable detection and formatting of inline elements like bold, italic, etc. |
| `enhanced_tables` | boolean | `true` | Enable enhanced table formatting |
| `html_for_complex_tables` | boolean | `true` | Use HTML for complex tables with merged cells |
| `add_simplified_fallback` | boolean | `true` | Add simplified markdown table as a comment for viewers that don't support HTML |
| `html_anchors` | boolean | `true` | Add HTML anchors to section headings for cross-references |
| `post_processing` | boolean | `true` | Apply post-processing to improve overall formatting |
| `validation` | boolean | `true` | Validate markdown output and report issues |
| `include_validation_report` | boolean | `false` | Include validation report as a comment at the end of the file |

## Example Output

The Enhanced Markdown Formatter produces more readable and structured output compared to the standard Markdown formatter. Here's an example of the differences:

### Standard Markdown Formatter

```markdown
# Section Title

This is a paragraph with some text.
This is still part of the same paragraph.

1. This is a list item.
2. This is another list item.

This is a table:
| Header 1 | Header 2 |
| --- | --- |
| Cell 1 | Cell 2 |
| Cell 3 | Cell 4 |
```

### Enhanced Markdown Formatter

```markdown
# Section Title <a id="section-title"></a>

This is a paragraph with some text. This is still part of the same paragraph.

1. This is a list item.
1. This is another list item.

| Header 1 | Header 2 |
| --- | ---: |
| Cell 1 | Cell 2 |
| Cell 3 | Cell 4 |

> **Note:** The Enhanced Markdown Formatter automatically detects and formats notes.

**Figure 1:** This is a figure caption that was automatically detected.
```

## Complex Table Handling

For complex tables with merged cells, the Enhanced Markdown Formatter will use HTML to preserve the structure:

```html
<table>
  <thead>
    <tr>
      <th rowspan="2">Header 1</th>
      <th colspan="2">Header 2</th>
    </tr>
    <tr>
      <th>Subheader 1</th>
      <th>Subheader 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Cell 1</td>
      <td>Cell 2</td>
      <td>Cell 3</td>
    </tr>
  </tbody>
</table>
```

## Implementation Details

The Enhanced Markdown Formatter extends the base `MarkdownFormatter` class and overrides the following methods:

- `format()`: Main entry point for formatting
- `_build_content_tree()`: Builds a hierarchical structure from flat sections
- `_format_section_to_markdown()`: Converts a section to markdown with enhanced formatting
- `_segment_content()`: Segments content into paragraphs, lists, and other elements
- `_format_table_to_markdown()`: Formats tables with support for complex structures

The formatter also adds several new methods for specialized formatting:

- `_identify_special_element()`: Detects notes, warnings, definitions, etc.
- `_identify_list_item()`: Detects and formats list items
- `_process_inline_formatting()`: Applies inline formatting for emphasis, code, etc.
- `_post_process_markdown()`: Improves overall formatting and readability
- `_validate_markdown()`: Validates the markdown output and reports issues

## Usage in Code

To use the Enhanced Markdown Formatter programmatically:

```python
from utils.pipeline.processors.formatters.factory import FormatterFactory, OutputFormat

# Create formatter with configuration
config = {
    "content_segmentation": True,
    "inline_formatting": True,
    "enhanced_tables": True
}
formatter = FormatterFactory.create_formatter(OutputFormat.ENHANCED_MARKDOWN, config)

# Format data
formatted_data = formatter.format(analyzed_data)

# Write to file
formatter.write(formatted_data, "output.md")
