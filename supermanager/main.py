import sys
import os
from .ui import DirViewerApp

def main():
    initial_dir = os.path.expanduser("~") # Default to home directory
    if len(sys.argv) > 1:
        initial_dir = sys.argv[1]
    
    DirViewerApp(initial_dir=initial_dir).run()

if __name__ == "__main__":
    main()
