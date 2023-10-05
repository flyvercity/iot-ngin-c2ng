import sys
from pathlib import Path


Path(sys.argv[1]).mkdir(parents=True, exist_ok=True)