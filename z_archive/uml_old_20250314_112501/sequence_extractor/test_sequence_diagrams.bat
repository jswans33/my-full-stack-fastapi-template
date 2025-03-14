@echo off
:: Script to test the sequence diagram generation functionality

echo Testing Sequence Diagram Generation
echo ===================================
echo.

:: Create output directory if it doesn't exist
if not exist test_output mkdir test_output

:: Test 1: YAML-based sequence diagrams
echo Test 1: YAML-based sequence diagrams
echo ------------------------------------

:: Check if the example YAML file exists
if exist examples\sequence_diagrams\auth_flow.yaml (
    echo Found example YAML file. Generating diagram...
    python -m utils.uml_generator.cli generate-sequence ^
        --file examples\sequence_diagrams\auth_flow.yaml ^
        --output test_output\yaml_auth_flow.puml
    
    if exist test_output\yaml_auth_flow.puml (
        echo √ Success: YAML-based diagram generated at test_output\yaml_auth_flow.puml
    ) else (
        echo × Error: Failed to generate YAML-based diagram
    )
) else (
    echo × Error: Example YAML file not found. Please ensure examples\sequence_diagrams\auth_flow.yaml exists.
)

echo.

:: Test 2: Static code analysis-based sequence diagrams
echo Test 2: Static code analysis-based sequence diagrams
echo --------------------------------------------------

:: Check if the example code file exists
if exist examples\sequence_example.py (
    echo Found example code file. Extracting sequence diagram...
    python -m utils.extract_sequence ^
        --dir examples ^
        --class UserService ^
        --method create_user ^
        --output test_output\code_create_user.puml
    
    if exist test_output\code_create_user.puml (
        echo √ Success: Code analysis-based diagram generated at test_output\code_create_user.puml
    ) else (
        echo × Error: Failed to generate code analysis-based diagram
    )
) else (
    echo × Error: Example code file not found. Please ensure examples\sequence_example.py exists.
)

echo.

:: Test 3: Run the full UML generator
echo Test 3: Running the full UML generator
echo ------------------------------------
echo This will generate all UML diagrams including sequence diagrams.
echo Running utils.run_uml_generator...

python -m utils.run_uml_generator

if exist docs\source\_generated_uml\sequence (
    echo √ Success: Sequence diagrams directory created
    
    :: Count the number of sequence diagrams
    setlocal enabledelayedexpansion
    set /a NUM_DIAGRAMS=0
    for %%f in (docs\source\_generated_uml\sequence\*.puml) do set /a NUM_DIAGRAMS+=1
    
    if !NUM_DIAGRAMS! gtr 0 (
        echo √ Success: !NUM_DIAGRAMS! sequence diagram(s) generated in docs\source\_generated_uml\sequence\
        echo Generated files:
        dir /b docs\source\_generated_uml\sequence\*.puml
    ) else (
        echo × Warning: No sequence diagrams found in docs\source\_generated_uml\sequence\
    )
    endlocal
) else (
    echo × Error: Sequence diagrams directory not created
)

echo.
echo Testing complete!
echo For more details on usage, see docs\source\sequence_diagram_usage.rst