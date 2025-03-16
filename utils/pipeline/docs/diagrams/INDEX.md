# Pipeline Architecture Documentation Index

This index file serves as the entry point for understanding the pipeline architecture. It provides links to all relevant documentation files and explains what information each contains.

## Core Documentation Files

| Document | Purpose | Key Information |
|----------|---------|-----------------|
| [README.md](README.md) | Main documentation entry point | Diagram numbering system, file listing, viewing instructions |
| [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) | High-level system overview | Key components, design patterns, technology stack |
| [DOCUMENT_FLOW_GUIDE.md](DOCUMENT_FLOW_GUIDE.md) | How documents flow through the system | Step-by-step processing stages with diagram references |
| [DIAGRAM_NAVIGATION_GUIDE.md](DIAGRAM_NAVIGATION_GUIDE.md) | How to navigate between related diagrams | Navigation maps, purpose-based diagram references |
| [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) | Mapping architecture to code | Code structure, interfaces, patterns, extension points |

## Getting Started

1. **New to the project?** Start with [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) for a high-level understanding.

2. **Want to understand data flow?** Read [DOCUMENT_FLOW_GUIDE.md](DOCUMENT_FLOW_GUIDE.md) to see how documents are processed.

3. **Looking for specific diagrams?** Use [DIAGRAM_NAVIGATION_GUIDE.md](DIAGRAM_NAVIGATION_GUIDE.md) to find relevant diagrams.

4. **Implementing or extending code?** Refer to [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for code structure guidance.

## Diagram Categories

The architecture is documented through several categories of diagrams:

1. **Overall Pipeline Architecture (01-XX)**
   - System components and their relationships
   - Complete data flow through the pipeline

2. **Document Classifier Component (02-XX)**
   - Classification strategies and structure
   - Document classification flow

3. **Formatter Component (03-XX)**
   - Output formatting system structure
   - Formatting process flow

4. **Verifier Component (04-XX)**
   - Output verification system structure
   - Verification process flow

5. **Schema Registry (05-XX)**
   - Schema management system structure
   - Schema validation flow

6. **PDF Document Processing (06-XX)**
   - PDF-specific processing use cases
   - PDF processing sequence
   - PDF classifier component details
   - PDF classification decision logic

## How This Documentation Is Organized

The documentation follows a **layered approach**:

1. **Conceptual Layer**: ARCHITECTURE_OVERVIEW.md provides the big picture
2. **Process Layer**: DOCUMENT_FLOW_GUIDE.md shows how data moves through the system
3. **Structural Layer**: Individual diagrams show detailed component structures
4. **Implementation Layer**: IMPLEMENTATION_GUIDE.md connects diagrams to code

This multi-layered approach allows both new and experienced developers to find the information they need at the appropriate level of detail.