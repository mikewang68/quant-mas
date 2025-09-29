#!/usr/bin/env python
# coding=utf-8

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and test the down2mongo script
if __name__ == "__main__":
    try:
        # Import the main function from down2mongo
        from utils.down2mongo import main

        print("Testing down2mongo script...")
        # Run the main function
        main()
        print("Test completed successfully!")

    except Exception as e:
        print(f"Error running down2mongo script: {e}")
        import traceback
        traceback.print_exc()

