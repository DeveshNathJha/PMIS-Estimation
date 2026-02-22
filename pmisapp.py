import sys
import os

# Ensure the root directory is in the path so we can import 'app'
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.main import main

if __name__ == "__main__":
    main()