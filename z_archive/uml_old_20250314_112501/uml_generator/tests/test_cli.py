"""Tests for command line interface."""

import pytest

from ..cli import parse_args


def test_file_argument():
    """Test parsing file argument."""
    args = parse_args(["-f", "test.py"])
    assert args.file == "test.py"
    assert not args.directory
    assert not args.app_dir


def test_directory_argument():
    """Test parsing directory argument."""
    args = parse_args(["-d", "test_dir"])
    assert args.directory == "test_dir"
    assert not args.file
    assert not args.app_dir


def test_app_dir_argument():
    """Test parsing app_dir argument."""
    args = parse_args(["--app-dir"])
    assert args.app_dir
    assert not args.file
    assert not args.directory


def test_recursive_flag():
    """Test parsing recursive flag."""
    args = parse_args(["-d", "test_dir", "--recursive"])
    assert args.recursive
    assert args.directory == "test_dir"


def test_output_directory():
    """Test parsing output directory."""
    args = parse_args(["-d", "test_dir", "-o", "output_dir"])
    assert args.output == "output_dir"


def test_format_option():
    """Test parsing format option."""
    args = parse_args(["-d", "test_dir", "--format", "plantuml"])
    assert args.format == "plantuml"


def test_subdirs_option():
    """Test parsing subdirs option."""
    args = parse_args(["-d", "test_dir", "--subdirs", "models", "services"])
    assert args.subdirs == ["models", "services"]


def test_verbosity_options():
    """Test parsing verbosity options."""
    args = parse_args(["-d", "test_dir", "-v"])
    assert args.verbose
    assert not args.quiet
    assert not args.debug

    args = parse_args(["-d", "test_dir", "-q"])
    assert args.quiet
    assert not args.verbose
    assert not args.debug

    args = parse_args(["-d", "test_dir", "--debug"])
    assert args.debug
    assert not args.verbose
    assert not args.quiet


def test_mutually_exclusive_inputs():
    """Test mutually exclusive input arguments."""
    with pytest.raises(SystemExit):
        parse_args(["-f", "test.py", "-d", "test_dir"])

    with pytest.raises(SystemExit):
        parse_args(["-f", "test.py", "--app-dir"])

    with pytest.raises(SystemExit):
        parse_args(["-d", "test_dir", "--app-dir"])


def test_mutually_exclusive_verbosity():
    """Test mutually exclusive verbosity arguments."""
    with pytest.raises(SystemExit):
        parse_args(["-d", "test_dir", "-v", "-q"])

    with pytest.raises(SystemExit):
        parse_args(["-d", "test_dir", "-v", "--debug"])

    with pytest.raises(SystemExit):
        parse_args(["-d", "test_dir", "-q", "--debug"])
