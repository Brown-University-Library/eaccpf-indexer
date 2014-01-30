"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import datetime

class Timer:
    """
    Time a procedure.
    """
    def __enter__(self):
        self.start = datetime.datetime.now()
        return self

    def __exit__(self, *args):
        self.interval = datetime.datetime.now() - self.start
        s = self.interval.seconds
        self.hours, remainder = divmod(s, 3600)
        self.minutes, self.seconds = divmod(remainder, 60)
