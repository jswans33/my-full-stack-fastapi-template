@echo off
REM pipeline_test.bat
REM Script to execute the document pipeline test plan

REM Set variables
set PIPELINE_DIR=C:\Repos\FCA-dashboard3\my-full-stack-fastapi-template\utils\pipeline
set SAMPLE_PDF=C:\Repos\FCA-dashboard3\my-full-stack-fastapi-template\utils\pipeline\data\tests\pdf\sample.pdf
set OUTPUT_DIR=C:\Repos\FCA-dashboard3\my-full-stack-fastapi-template\utils\pipeline\data\output
set REPORT_PATH=%OUTPUT_DIR%\report.json

REM Create output directory if it doesn't exist
if not exist %OUTPUT_DIR% (
    mkdir %OUTPUT_DIR%
    echo Created output directory: %OUTPUT_DIR%
)

REM Verify sample PDF exists
if not exist %SAMPLE_PDF% (
    echo Error: Sample PDF not found at %SAMPLE_PDF%
    exit /b 1
)

REM Navigate to pipeline directory
cd %PIPELINE_DIR%

REM Check Python version
python --version

REM Run the pipeline with basic settings
echo Running pipeline with basic settings...
python -m utils.pipeline.run_pipeline --file %SAMPLE_PDF% --output %OUTPUT_DIR%

REM Run with multiple output formats
echo Running pipeline with multiple output formats...
python -m utils.pipeline.run_pipeline --file %SAMPLE_PDF% --output %OUTPUT_DIR% --formats json,markdown

REM Run with processing report
echo Running pipeline with processing report...
python -m utils.pipeline.run_pipeline --file %SAMPLE_PDF% --output %OUTPUT_DIR% --report %REPORT_PATH%

REM Verify output files
echo Verifying output files...
dir %OUTPUT_DIR%

echo Test execution completed.
