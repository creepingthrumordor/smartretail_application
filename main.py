"""Launch the dashboard from the project root or this package directory."""
from pathlib import Path
import sys

# When launched as ``python main.py`` from inside smartretail/, add the project
# root so the package's absolute imports resolve consistently.
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from smartretail.gui.app import DashboardWindow
def main():DashboardWindow().start()
if __name__=='__main__':main()
