#!/usr/bin/env python3
"""
Example Python file to demonstrate Ruff formatting and linting.

This file intentionally contains various style issues that Ruff can fix.
To see Ruff in action, run:
    ruff check examples/workspace-setup/example.py --fix
    ruff format examples/workspace-setup/example.py
"""

import json
import sys
from typing import Any


# Function with various style issues
def process_data(
    data_input: list[dict[str, Any]],
    filter_key: str | None = None,
    debug: bool = False,
) -> dict[str, Any]:
    """Process the input data and return a summary.

    Args:
        data_input: List of data dictionaries to process
        filter_key: Optional key to filter results
        debug: Whether to print debug information

    Returns:
        A dictionary with processed results
    """
    result = {"total": len(data_input), "processed": 0, "filtered": 0}

    # Unnecessary variable
    items = data_input

    for item in items:
        # Unused variable
        item_id = item.get("id")

        # Print statement that should be logged
        if debug == True:
            print(f"Processing item: {item}")

        # Inefficient list comprehension
        filtered_values = [x for x in item.values() if x is not None]

        # Could use dict comprehension
        clean_item = {}
        for k, v in item.items():
            if v is not None:
                clean_item[k] = v

        # Filter logic
        if filter_key != None and filter_key in item:
            result["filtered"] += 1
            continue

        result["processed"] += 1

    return result


# Class with style issues
class DataProcessor:
    def __init__(self, config_file=None):
        self.config = {}
        if config_file != None:
            with open(config_file) as f:
                self.config = json.load(f)

        # Unused attribute
        self.version = "1.0.0"

    # Method with too many arguments
    def transform_data(
        self,
        data,
        normalize=False,
        validate=True,
        convert_dates=False,
        remove_nulls=True,
        add_metadata=False,
        format_strings=True,
    ):
        """Transform the data based on various options."""
        if normalize == True:
            # Implement normalization
            pass

        # Redundant else after return
        if not validate:
            return data
        # Validate data
        return data


# Main execution with style issues
if __name__ == "__main__":
    # Unnecessary list conversion
    args = list(sys.argv[1:])

    # Inefficient string concatenation
    message = "Running " + "example" + " with " + str(len(args)) + " arguments"

    # Unused variable
    debug_mode = True

    # Create sample data
    sample_data = [
        {"id": 1, "name": "Item 1", "value": 100, "active": True},
        {"id": 2, "name": "Item 2", "value": None, "active": False},
        {"id": 3, "name": "Item 3", "value": 300, "active": None},
    ]

    # Process data
    result = process_data(sample_data, debug=True)

    # Print result
    print(f"Result: {result}")
