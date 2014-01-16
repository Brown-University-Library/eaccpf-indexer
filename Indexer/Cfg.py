"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import inspect
import sys

def is_debugging():
  for frame in inspect.stack():
    if frame[1].endswith("pydevd.py"):
      return True
  return False

## Globals
LOG_EXC_INFO = True if is_debugging() else False
