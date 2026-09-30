"""Play Ninja Turtle sprite-sheet animations in sequence.

The source sheet has uneven frame sizes and animation lengths, so each frame
is cropped and its connected sheet background is made transparent at startup.
"""

from collections import Counter, deque
from pathlib import Path
import struct
