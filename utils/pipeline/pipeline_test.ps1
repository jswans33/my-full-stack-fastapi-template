# pipeline_test.ps1
# Script to execute the document pipeline test plan

# Set variables
$PIPELINE_DIR = "C:\Repos\FCA-dashboard3\my-full-stack-fastapi-template\utils\pipeline"
$SAMPLE_PDF = "C:\Repos\FCA-dashboard3\my-full-stack-fastapi-template\utils\pipeline\data\tests\pdf\sample.pdf"
$OUTPUT_DIR = "C:\Repos\FCA-dashboard3\my-full-stack-fastapi-template\utils\pipeline\data\output"
$REPORT_PATH = "$OUTPUT_DIR\report.json"

# Create output directory if it doesn't exist
if (-not (Test-Path $OUTPUT_DIR)) {
    New-Item -ItemType Directory -Path $OUTPUT_DIR
    Write-Host "Created output directory: $OUTPUT_DIR"
}

# Verify sample PDF exists
if (-not (Test-Path $SAMPLE_PDF)) {
    Write-Host "Error: Sample PDF not found at $SAMPLE_PDF" -ForegroundColor Red
    exit 1
}

# Navigate to pipeline directory
Set-Location $PIPELINE_DIR

# Check Python version
$pythonVersion = python --version
Write-Host "Using $pythonVersion"

# Run the pipeline with basic settings
Write-Host "Running pipeline with basic settings..." -ForegroundColor Green
python -m utils.pipeline.run_pipeline --file $SAMPLE_PDF --output $OUTPUT_DIR

# Run with multiple output formats
Write-Host "Running pipeline with multiple output formats..." -ForegroundColor Green
python -m utils.pipeline.run_pipeline --file $SAMPLE_PDF --output $OUTPUT_DIR --formats json,markdown

# Run with processing report
Write-Host "Running pipeline with processing report..." -ForegroundColor Green
python -m utils.pipeline.run_pipeline --file $SAMPLE_PDF --output $OUTPUT_DIR --report $REPORT_PATH

# Verify output files
Write-Host "Verifying output files..." -ForegroundColor Green
$outputFiles = Get-ChildItem $OUTPUT_DIR
Write-Host "Found $($outputFiles.Count) files in output directory:"
foreach ($file in $outputFiles) {
    Write-Host "- $($file.Name)"
}

Write-Host "Test execution completed." -ForegroundColor Green
