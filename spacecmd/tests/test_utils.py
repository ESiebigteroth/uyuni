# coding: utf-8
"""
Test spacecmd.utils
"""
from unittest.mock import MagicMock, patch
import pytest
from helpers import shell, assert_expect, assert_list_args_expect, assert_args_expect
import spacecmd.utils
from xmlrpc import client as xmlrpclib
import os
import tempfile
import shutil
import datetime
import pickle
import hashlib
import time


class TestSCUtilsCacheIntegration:
    """
    Fusion integration test for saving and loading cache file.
    This creates and saves cache, loads it and expires it into
    a temporary directory.
    """
    def setup_method(self):
        """
        Setup test

        :return:
        """
        self.data = {"key": hashlib.sha256(str(time.time()).encode("utf-8")).hexdigest()}
        self.temp = tempfile.mkdtemp()
        self.expiration = datetime.datetime(2019, 1, 1, 10, 30, 45)
        self.cachefile = os.path.join(self.temp, "spacecmd.cache")

    def teardown_method(self):
        """
        Teardown method

        :return:
        """
        shutil.rmtree(self.temp)
        self.data.clear()
        self.expiration = None
        self.cachefile = None

    def test_save_cache(self):
        """
        Save cache.

        :return:
        """
        spacecmd.utils.save_cache(cachefile=self.cachefile, data=self.data, expire=self.expiration)
        assert os.path.exists(self.cachefile)
        out = pickle.load(open(self.cachefile, "rb"))

        assert "expire" in out
        assert "expire" not in self.data
        assert out["expire"] == self.expiration
        assert self.data["key"] == out["key"]

    @patch("spacecmd.utils.open", MagicMock(side_effect=IOError("Wrong polarity on neutron flow")))
    def test_save_cache_io_error(self):
        """
        Handle saving cache when IOError happens.

        :return:
        """
        logger = MagicMock()
        with patch("spacecmd.utils.logging", logger) as lgr:
            spacecmd.utils.save_cache(cachefile=self.cachefile,
                                      data=self.data, expire=self.expiration)
        assert logger.error.called
        assert_args_expect(logger.error.call_args_list,
                           [(("Couldn't write to %s", self.cachefile,), {})])

    def test_load_cache(self):
        """
        Load cache.

        :return:
        """
        spacecmd.utils.save_cache(cachefile=self.cachefile, data=self.data, expire=self.expiration)

        assert os.path.exists(self.cachefile)

        out, expiration = spacecmd.utils.load_cache(self.cachefile)

        assert "expire" not in out
        assert expiration == self.expiration
        assert self.data["key"] == out["key"]

    def test_load_corrupted_cache(self):
        """
        Load corrupted cache.

        :return:
        """
        with open(self.cachefile, "wb") as che:
            che.write(b"\x00\x00\x00\x00")
        assert os.path.exists(self.cachefile)

        out, expiration = spacecmd.utils.load_cache(self.cachefile)

        assert out == {}
        assert expiration != self.expiration is not None
        assert not os.path.exists(self.cachefile)


class TestSCUtils:
    """
    Test suite for utils functions.
    """

    def test_parse_command_arguments(self):
        """
        Test argument parser.
        :return:
        """

        arg_parser = spacecmd.utils.get_argument_parser()
        args, opts = spacecmd.utils.parse_command_arguments("one two three", argument_parser=arg_parser, glob=True)
        assert args == ["one", "two", "three"] == opts.leftovers

        arg_parser.add_argument("-a", "--arg")
        args, opts = spacecmd.utils.parse_command_arguments("--arg idea", argument_parser=arg_parser, glob=True)

        assert opts.leftovers == []
        assert opts.arg == "idea"

    def test_is_interactive(self):
        """
        Test is_interactive check
        :return:
        """

        arg_parser = spacecmd.utils.get_argument_parser()
        args, opts = spacecmd.utils.parse_command_arguments("arg", argument_parser=arg_parser, glob=True)
        assert not spacecmd.utils.is_interactive(opts)

        arg_parser.add_argument("-a", "--arg")
        args, opts = spacecmd.utils.parse_command_arguments("--arg idea", argument_parser=arg_parser, glob=True)
        assert not spacecmd.utils.is_interactive(opts)

        args, opts = spacecmd.utils.parse_command_arguments("", argument_parser=arg_parser, glob=True)
        assert spacecmd.utils.is_interactive(opts)

    def test_filter_results(self):
        """
        Test results filtering.

        :return:
        """
        out = spacecmd.utils.filter_results(["space", "spacecmd", "cmdspace", "somespacecmd",
                                             "somecmd", "cmdsome", "piglet"],
                                            ["space*", "pig"], search=True)
        assert out == ['space', 'spacecmd', 'cmdspace', 'somespacecmd', 'piglet']

        out = spacecmd.utils.filter_results(["space", "spacecmd", "cmdspace", "somespacecmd",
                                             "somecmd", "cmdsome", "piglet"],
                                            ["space*", "pig"], search=False)
        assert out == ['space']

    @patch("spacecmd.utils.mkstemp", MagicMock(return_value=(1, "test",)))
    @patch("spacecmd.utils.os.fdopen", MagicMock(side_effect=IOError("Electromagnetic energy loss")))
    def test_editor_ioerror_handle(self):
        """
        Test to handle IOError by an external editor when the temporary file cannot be written.

        :return:
        """
        spawner = MagicMock()
        logger = MagicMock()
        with patch("spacecmd.utils.os.spawnlp", spawner) as spw, \
            patch("spacecmd.utils.logging", logger) as lgr:
            spacecmd.utils.editor("clock speed adjustments")

        assert logger.warning.called
        assert logger.error.called
        assert not spawner.called

    @patch("spacecmd.utils.mkstemp", MagicMock(return_value=(1, "test",)))
    @patch("spacecmd.utils.os.fdopen", MagicMock(return_value=MagicMock()))
    @patch("spacecmd.utils.os.environ", {})
    def test_editor_editor_failed(self):
        """
        Test to handle editor launch failures.

        :return:
        """
        spawner = MagicMock(return_value=42)
        logger = MagicMock()
        with patch("spacecmd.utils.os.spawnlp", spawner) as spw, \
            patch("spacecmd.utils.logging", logger) as lgr:
            spacecmd.utils.editor("clock speed adjustments")

        assert not logger.warning.called
        assert logger.error.called
        assert spawner.called

        assert_args_expect(logger.error.call_args_list,
                           [(('Editor "%s" exited with code %i', "vim", 42), {}),
                            (('Editor "%s" exited with code %i', "vi", 42), {}),
                            (('Editor "%s" exited with code %i', "emacs", 42), {}),
                            (('Editor "%s" exited with code %i', "nano", 42), {}),
                            (('No editors found',), {})])