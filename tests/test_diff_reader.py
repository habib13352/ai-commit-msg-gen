import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from diff_reader import extract_changed_files


def test_extract_files_from_rename_diff():
    diff_text = (
        "diff --git a/old.py b/new.py\n"
        "similarity index 100%\n"
        "rename from old.py\n"
        "rename to new.py\n"
    )
    files = extract_changed_files(diff_text)
    assert set(files) == {"old.py", "new.py"}

