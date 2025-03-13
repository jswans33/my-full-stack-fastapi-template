import os
import sys

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import works correctly
from utils.uml_generator.cli import main

if __name__ == "__main__":
    main()
