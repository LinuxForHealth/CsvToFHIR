
import os
from functools import partial

from deepdiff import DeepDiff

# base resource directory for "file fixtures" (sample x12 transactions)
resources_directory = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "resources"
)

deep_diff = partial(DeepDiff, ignore_order=True)
