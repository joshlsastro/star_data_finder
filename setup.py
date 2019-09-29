"""IMPORTANT: You must already have Python 3 to run this."""

import os
import sys

py = sys.executable
install = py + " -m pip install "
os.system(install + "--upgrade pip")
os.system(install + "astropy")
