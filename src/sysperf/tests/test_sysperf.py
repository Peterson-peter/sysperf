import pytest
import sysperf


def test_project_defines_author_and_version():
    assert hasattr(sysperf, '__author__')
    assert hasattr(sysperf, '__version__')
