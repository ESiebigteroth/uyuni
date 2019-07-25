# coding: utf-8
"""
Configchannel module unit tests.
"""

import os
from unittest.mock import MagicMock, patch, mock_open
from helpers import shell, assert_expect, assert_list_args_expect, assert_args_expect
import spacecmd.configchannel
from xmlrpc import client as xmlrpclib
import datetime


class TestSCConfigChannel:
    """
    Test configuration channel.
    """
    def test_configchannel_list_noret(self, shell):
        """
        Test configuration channel list, no data return.

        :param shell:
        :return:
        """
        shell.client.configchannel.listGlobals = MagicMock(return_value=[
            {"label": "base_channel"}, {"label": "boese_channel"},
            {"label": "other_channel"}, {"label": "ze_channel"},
            {"label": "and_some_channel"}, {"label": "another_channel"}
        ])
        mprint = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt:
            ret = spacecmd.configchannel.do_configchannel_list(shell, "", doreturn=False)

        assert ret is None
        assert mprint.called
        assert shell.client.configchannel.listGlobals.called

        assert_expect(mprint.call_args_list,
                      'and_some_channel\nanother_channel\nbase_channel'
                      '\nboese_channel\nother_channel\nze_channel')

    def test_configchannel_list_data(self, shell):
        """
        Test configuration channel list, return data.

        :param shell:
        :return:
        """
        shell.client.configchannel.listGlobals = MagicMock(return_value=[
            {"label": "base_channel"}, {"label": "boese_channel"},
            {"label": "other_channel"}, {"label": "ze_channel"},
            {"label": "and_some_channel"}, {"label": "another_channel"}
        ])
        mprint = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt:
            ret = spacecmd.configchannel.do_configchannel_list(shell, "", doreturn=True)

        assert not mprint.called
        assert ret is not None
        assert shell.client.configchannel.listGlobals.called
        assert ret == ['and_some_channel', 'another_channel', 'base_channel',
                       'boese_channel', 'other_channel', 'ze_channel']

    def test_configchannel_listsystems_api_version_handling(self, shell):
        """
        Test configchannel listsystems function. Check version limitation.

        :param shell:
        :return:
        """
        shell.check_api_version = MagicMock(return_value=False)
        mprint = MagicMock()
        logger = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_listsystems(shell, "")

        assert not mprint.called
        assert not shell.client.configchannel.listSubscribedSystems.called
        assert not shell.help_configchannel_listsystems.called

    def test_configchannel_listsystems_api_noarg(self, shell):
        """
        Test configchannel listsystems function. No arguments passed.

        :param shell:
        :return:
        """
        shell.check_api_version = MagicMock(return_value=True)
        mprint = MagicMock()
        logger = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_listsystems(shell, "")

        assert not mprint.called
        assert not shell.client.configchannel.listSubscribedSystems.called
        assert shell.help_configchannel_listsystems.called

    def test_configchannel_listsystems_api_sorted_output(self, shell):
        """
        Test configchannel listsystems function. Output must be sorted.

        :param shell:
        :return:
        """
        shell.client.configchannel.listSubscribedSystems = MagicMock(
            return_value=[
                {"name": "sisteme"}, {"name": "system"}, {"name": "exbox"},
                {"name": "zitrix"}, {"name": "paystation-4"}, {"name": "azure"},
                {"name": "quakearena"}, {"name": "awsbox"}, {"name": "beigebox"},
            ]
        )
        shell.check_api_version = MagicMock(return_value=True)
        mprint = MagicMock()
        logger = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_listsystems(shell, "some_channel")

        assert not shell.help_configchannel_listsystems.called
        assert mprint.called
        assert shell.client.configchannel.listSubscribedSystems.called
        assert_expect(mprint.call_args_list,
                      'awsbox\nazure\nbeigebox\nexbox\npaystation-4'
                      '\nquakearena\nsisteme\nsystem\nzitrix')

    def test_configchannel_listfiles_noarg(self, shell):
        """
        Test configchannel_listfiles function. No args.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_listfiles(shell, "")

        assert not shell.client.configchannel.listFiles.called
        assert not mprint.called
        assert shell.help_configchannel_listfiles.called

    def test_configchannel_listfiles_sorted_data(self, shell):
        """
        Test configchannel_listfiles function. Data is sorted for STDOUT.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.client.configchannel.listFiles = MagicMock(return_value=[
            {"path": "/tmp/somefile.txt"}, {"path": "/tmp/zypper.rpm"},
            {"path": "/tmp/aaa_base.rpm"}, {"path": "/tmp/someother.txt"},
            {"path": "/etc/whatever.conf"}, {"path": "/etc/ssh.conf"},
        ])
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            data = spacecmd.configchannel.do_configchannel_listfiles(shell, "some_channel")

        assert not shell.help_configchannel_listfiles.called
        assert shell.client.configchannel.listFiles.called
        assert mprint.called
        assert_expect(mprint.call_args_list,
                      "/etc/ssh.conf\n/etc/whatever.conf\n/tmp/aaa_base.rpm"
                      "\n/tmp/somefile.txt\n/tmp/someother.txt\n/tmp/zypper.rpm")

    def test_configchannel_listfiles_sorted_data_out(self, shell):
        """
        Test configchannel_listfiles function. Data is sorted as a type.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.client.configchannel.listFiles = MagicMock(return_value=[
            {"path": "/tmp/somefile.txt"}, {"path": "/tmp/zypper.rpm"},
            {"path": "/tmp/aaa_base.rpm"}, {"path": "/tmp/someother.txt"},
            {"path": "/etc/whatever.conf"}, {"path": "/etc/ssh.conf"},
        ])
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            data = spacecmd.configchannel.do_configchannel_listfiles(shell, "some_channel", doreturn=True)

        assert not mprint.called
        assert not shell.help_configchannel_listfiles.called
        assert shell.client.configchannel.listFiles.called

        assert data == ['/etc/ssh.conf', '/etc/whatever.conf', '/tmp/aaa_base.rpm',
                        '/tmp/somefile.txt', '/tmp/someother.txt', '/tmp/zypper.rpm']

    def test_configchannel_forcedeploy_noargs(self, shell):
        """
        Test configchannel_forcedeploy function. No arguments.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_forcedeploy(shell, "")

        assert not mprint.called
        assert not logger.error.called
        assert not logger.info.called
        assert not logger.warning.called
        assert not shell.client.configchannel.listFiles.called
        assert not shell.client.configchannel.listSubscribedSystems.called
        assert not shell.client.configchannel.deployAllSystems.called
        assert shell.help_configchannel_forcedeploy.called

    def test_configchannel_forcedeploy_too_much_args(self, shell):
        """
        Test configchannel_forcedeploy function. Too much arguments.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_forcedeploy(
                shell, "base_channel illegally_entered_channel")

        assert not mprint.called
        assert not logger.error.called
        assert not logger.info.called
        assert not logger.warning.called
        assert not shell.client.configchannel.listFiles.called
        assert not shell.client.configchannel.listSubscribedSystems.called
        assert not shell.client.configchannel.deployAllSystems.called
        assert shell.help_configchannel_forcedeploy.called

    def test_configchannel_forcedeploy_no_files(self, shell):
        """
        Test configchannel_forcedeploy function. No files found (or incomplete data).

        :param shell:
        :return:
        """
        shell.client.configchannel.listFiles = MagicMock(return_value=[
            {"pfad": "/der/hund"},
        ])
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_forcedeploy(shell, "base_channel")

        assert not shell.help_configchannel_forcedeploy.called
        assert not logger.error.called
        assert not logger.info.called
        assert not logger.warning.called
        assert not shell.client.configchannel.listSubscribedSystems.called
        assert not shell.client.configchannel.deployAllSystems.called
        assert shell.client.configchannel.listFiles.called
        assert mprint.called
        assert_expect(mprint.call_args_list,
                      "No files within selected configchannel.")

    def test_configchannel_forcedeploy_no_systems(self, shell):
        """
        Test configchannel_forcedeploy function. No subscribed systems.

        :param shell:
        :return:
        """
        shell.client.configchannel.listFiles = MagicMock(return_value=[
            {"path": "/tmp/file1.txt"},
            {"path": "/tmp/file2.txt"},
        ])
        shell.client.configchannel.listSubscribedSystems(return_value=[])
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_forcedeploy(shell, "base_channel")

        assert not shell.help_configchannel_forcedeploy.called
        assert not logger.error.called
        assert not logger.info.called
        assert not logger.warning.called
        assert not shell.client.configchannel.deployAllSystems.called
        assert shell.client.configchannel.listSubscribedSystems.called
        assert shell.client.configchannel.listFiles.called
        assert mprint.called
        assert_expect(mprint.call_args_list,
                      "Channel has no subscribed Systems")

    def test_configchannel_forcedeploy_deploy_output(self, shell):
        """
        Test configchannel_forcedeploy function. Output test.

        :param shell:
        :return:
        """
        shell.client.configchannel.listFiles = MagicMock(return_value=[
            {"path": "/tmp/file1.txt"},
            {"path": "/tmp/file2.txt"},
        ])
        shell.client.configchannel.listSubscribedSystems = MagicMock(return_value=[
            {"name": "butterfly.acme.org"},
            {"name": "beigebox.acme.org"},
        ])
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_forcedeploy(shell, "base_channel")

        assert not shell.help_configchannel_forcedeploy.called
        assert not logger.error.called
        assert not logger.info.called
        assert not logger.warning.called
        assert shell.client.configchannel.deployAllSystems.called
        assert shell.client.configchannel.listSubscribedSystems.called
        assert shell.client.configchannel.listFiles.called
        assert mprint.called
        assert_expect(mprint.call_args_list,
                      'Force deployment of the following configfiles:',
                      '==============================================',
                      '/tmp/file1.txt\n/tmp/file2.txt', '\nOn these systems:',
                      '=================', 'beigebox.acme.org\nbutterfly.acme.org')

    def test_configchannel_filedetails_no_args(self, shell):
        """
        Test configchannel_filedetails function with no arguments.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_filedetails(shell, "")

        assert not shell.client.configchannel.lookupFileInfo.called
        assert not shell.do_configchannel_listfiles.called
        assert not mprint.called
        assert not logger.warning.called
        assert not logger.error.called
        assert not logger.info.called
        assert shell.help_configchannel_filedetails.called

    def test_configchannel_filedetails_wrong_amt_args(self, shell):
        """
        Test configchannel_filedetails function with wrong amount of arguments.

        :param shell:
        :return:
        """
        for args in ["one", "one two three four", "one two three four five"]:
            mprint = MagicMock()
            logger = MagicMock()
            shell.user_confirm = MagicMock()
            with patch("spacecmd.configchannel.print", mprint) as prt, \
                    patch("spacecmd.configchannel.logging", logger) as lgr:
                spacecmd.configchannel.do_configchannel_filedetails(shell, args)

            assert not shell.client.configchannel.lookupFileInfo.called
            assert not shell.do_configchannel_listfiles.called
            assert not mprint.called
            assert not logger.warning.called
            assert not logger.error.called
            assert not logger.info.called
            assert shell.help_configchannel_filedetails.called

    def test_configchannel_filedetails_wrong_revision(self, shell):
        """
        Test configchannel_filedetails function with wrong amount of arguments.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_filedetails(
                shell, "base_channel /tmp/file.txt kaboom")

        assert not shell.client.configchannel.lookupFileInfo.called
        assert not shell.do_configchannel_listfiles.called
        assert not mprint.called
        assert not logger.warning.called
        assert not logger.info.called
        assert not shell.help_configchannel_filedetails.called
        assert logger.error.called

        assert_args_expect(logger.error.call_args_list,
                           [(('Invalid revision: %s', 'kaboom'), {})])

    def test_configchannel_filedetails_invalid_files(self, shell):
        """
        Test configchannel_filedetails function with invalid files.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        shell.do_configchannel_listfiles = MagicMock(return_value=[
            "/tmp/valid.file", "/tmp/another-valid.file",
        ])
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_filedetails(
                shell, "base_channel /tmp/file.txt")

        assert not shell.client.configchannel.lookupFileInfo.called
        assert not mprint.called
        assert not logger.info.called
        assert not shell.help_configchannel_filedetails.called
        assert not logger.error.called
        assert shell.do_configchannel_listfiles.called
        assert logger.warning.called

    def test_configchannel_filedetails_with_invalid_revision(self, shell):
        """
        Test configchannel_filedetails function with invalid revision

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        shell.do_configchannel_listfiles = MagicMock(return_value=[
            "/tmp/valid.file", "/tmp/another-valid.file", "/tmp/file.txt"
        ])
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_filedetails(
                shell, "base_channel /tmp/file.txt 0.3")

        assert not logger.info.called
        assert not shell.help_configchannel_filedetails.called
        assert not logger.warning.called
        assert not shell.client.configchannel.lookupFileInfo.called
        assert not mprint.called
        assert not shell.do_configchannel_listfiles.called
        assert logger.error.called

        assert_args_expect(logger.error.call_args_list,
                           [(("Invalid revision: %s", "0.3"), {})])

    def test_configchannel_filedetails_with_correct_revision_na(self, shell):
        """
        Test configchannel_filedetails function with correct revision, data N/A.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        shell.client.configchannel.lookupFileInfo = MagicMock(return_value={
            "path": "/tmp.file.txt"
        })
        shell.do_configchannel_listfiles = MagicMock(return_value=[
            "/tmp/valid.file", "/tmp/another-valid.file", "/tmp/file.txt"
        ])
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            result = spacecmd.configchannel.do_configchannel_filedetails(
                shell, "base_channel /tmp/file.txt 3")

        assert not logger.info.called
        assert not shell.help_configchannel_filedetails.called
        assert not logger.warning.called
        assert not logger.error.called
        assert not mprint.called
        assert shell.client.configchannel.lookupFileInfo.called
        assert shell.do_configchannel_listfiles.called

        assert result is not None
        assert result == ['Path:     /tmp.file.txt', 'Type:     N/A', 'Revision: N/A', 'Created:  N/A',
                          'Modified: N/A', '', 'Owner:           N/A', 'Group:           N/A',
                          'Mode:            N/A', 'SELinux Context: N/A']

    def test_configchannel_filedetails_with_correct_revision_data(self, shell):
        """
        Test configchannel_filedetails function with correct revision, data available.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.user_confirm = MagicMock()
        shell.client.configchannel.lookupFileInfo = MagicMock(return_value={
            "path": "/tmp.file.txt", "type": "file", "revision": "3",
            "creation": "2019.01.01", "modified": "2019.01.02",
            "owner": "Fred", "group": "lusers", "permissions_mode": "0700",
            "selinux_ctx": "system_u", "sha256": "1234567", "binary": False,
            "contents": "Improper keyboard linear orientation"
        })
        shell.do_configchannel_listfiles = MagicMock(return_value=[
            "/tmp/valid.file", "/tmp/another-valid.file", "/tmp/file.txt"
        ])
        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            result = spacecmd.configchannel.do_configchannel_filedetails(
                shell, "base_channel /tmp/file.txt 3")

        assert not logger.info.called
        assert not shell.help_configchannel_filedetails.called
        assert not logger.warning.called
        assert not logger.error.called
        assert not mprint.called
        assert shell.client.configchannel.lookupFileInfo.called
        assert shell.do_configchannel_listfiles.called

        assert result is not None
        assert result == ['Path:     /tmp.file.txt', 'Type:     file', 'Revision: 3', 'Created:  2019.01.01',
                          'Modified: 2019.01.02', '', 'Owner:           Fred', 'Group:           lusers',
                          'Mode:            0700', 'SELinux Context: system_u', 'SHA256:          1234567',
                          'Binary:          False', '', 'Contents', '--------', 'Improper keyboard linear orientation']

    def test_configchannel_backup_noargs(self, shell):
        """
        Test configchannel_backup function without args.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        _datetime = MagicMock()
        _os = MagicMock()
        with patch("spacecmd.configchannel.open", create=True) as mopen, \
                patch("spacecmd.configchannel.os", _os) as mck_os, \
                patch("spacecmd.configchannel.print", mprint) as mck_prt, \
                patch("spacecmd.configchannel.logging", mprint) as mck_lgr:
            mopen.return_value = MagicMock(spec=open)
            spacecmd.configchannel.do_configchannel_backup(shell, "")

        assert not mprint.called
        assert not logger.error.called
        assert not mopen.called
        assert not shell.client.configchannel.lookupFileInfo.called
        assert not shell.do_configchannel_listfiles.called
        assert not _os.path.expanduser.called
        assert not _os.path.join.called
        assert not _datetime.called
        assert shell.help_configchannel_backup.called

    def test_configchannel_backup_outputdir_failure(self, shell):
        """
        Test configchannel_backup function with output directory failed to be created.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        _datetime = MagicMock()
        _os = MagicMock()
        _os.path.expanduser = MagicMock(return_value="/dev/null/bofh")
        _os.path.isdir = MagicMock(return_value=False)
        _os.makedirs = MagicMock(side_effect=OSError("Fractal learning curve"))
        with patch("spacecmd.configchannel.open", create=True) as mopen, \
                patch("spacecmd.configchannel.os", _os) as mck_os, \
                patch("spacecmd.configchannel.dir", mprint) as mck_prt, \
                patch("spacecmd.configchannel.logging", logger) as mck_lgr:
            mopen.return_value = MagicMock(spec=open)
            spacecmd.configchannel.do_configchannel_backup(shell, "base_channel /tmp/somewhere")

        assert not shell.help_configchannel_backup.called
        assert not mprint.called
        assert not mopen.called
        assert not shell.client.configchannel.lookupFileInfo.called
        assert not shell.do_configchannel_listfiles.called
        assert not _os.path.join.called
        assert not _datetime.called
        assert _os.path.expanduser.called
        assert logger.error.called

        assert_args_expect(logger.error.call_args_list,
                           [(('Could not create output directory: %s',
                              'Fractal learning curve'), {})])

    def test_configchannel_backup_outputdir_metainfo_failure(self, shell):
        """
        Test configchannel_backup function with output directory, failed to create metainfo.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        _datetime = MagicMock()
        _os = MagicMock()
        _os.path.expanduser = MagicMock(return_value="/dev/null/bofh")
        _os.path.isdir = MagicMock(return_value=False)
        _os.path.join = os.path.join
        _os.makedirs = MagicMock()
        with patch("spacecmd.configchannel.open", MagicMock(side_effect=IOError("Bugs in the RAID"))) as mopen, \
                patch("spacecmd.configchannel.os", _os) as mck_os, \
                patch("spacecmd.configchannel.print", mprint) as mck_prt, \
                patch("spacecmd.configchannel.logging", logger) as mck_lgr:
            spacecmd.configchannel.do_configchannel_backup(shell, "base_channel /tmp/somewhere")

        assert not shell.help_configchannel_backup.called
        assert not mprint.called
        assert not _datetime.called
        assert mopen.called
        assert shell.client.configchannel.lookupFileInfo.called
        assert shell.do_configchannel_listfiles.called
        assert _os.path.expanduser.called
        assert logger.error.called

        assert_args_expect(logger.error.call_args_list,
                           [(('Could not create "%s" file: %s',
                              '/dev/null/bofh/.metainfo',
                              'Bugs in the RAID'), {})])

    def test_configchannel_details_noargs(self, shell):
        """
        Test configchannel_details without directory.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()

        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            out = spacecmd.configchannel.do_configchannel_details(shell, "")

        assert out is None
        assert not mprint.called
        assert not shell.client.configchannel.getDetails.called
        assert not shell.client.configchannel.listFiles.called
        assert shell.help_configchannel_details.called

    def test_configchannel_details_channel(self, shell):
        """
        Test configchannel_details.

        :param shell:
        :return:
        """
        mprint = MagicMock()
        logger = MagicMock()
        shell.client.configchannel.getDetails = MagicMock(return_value={
            "label": "base_channel", "name": "Base Channel",
            "description": "Base channel with some stuff",
            "configChannelType": {"label": "Stuff"}
        })
        shell.client.configchannel.listFiles = MagicMock(return_value=[
            {"path": "/dev/null/vim.rpm"},
            {"path": "/dev/null/pico.rpm"},
            {"path": "/dev/null/java.rpm"},
        ])

        with patch("spacecmd.configchannel.print", mprint) as prt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            out = spacecmd.configchannel.do_configchannel_details(shell, "base_channel")

        assert not mprint.called
        assert not shell.help_configchannel_details.called
        assert out is not None
        assert shell.client.configchannel.getDetails.called
        assert shell.client.configchannel.listFiles.called

        assert out == ['Label:       base_channel', 'Name:        Base Channel',
                       'Description: Base channel with some stuff', 'Type:        Stuff', '',
                       'Files', '-----', '/dev/null/vim.rpm', '/dev/null/pico.rpm', '/dev/null/java.rpm']

    def test_configchannel_create_noargs(self, shell):
        """
        Test configchannel_create, without arguments (turns into interactive).

        :param shell:
        :return:
        """
        puser = MagicMock(side_effect=[
            "John Smith", "config_channel", "Not ISO 9000 compliant", "normal",
        ])
        with patch("spacecmd.configchannel.prompt_user", puser) as pmt:
            spacecmd.configchannel.do_configchannel_create(shell, "")

        assert puser.called
        assert shell.client.configchannel.create.called

        assert_args_expect(shell.client.configchannel.create.call_args_list,
                           [((shell.session, 'config_channel', 'John Smith',
                              'Not ISO 9000 compliant', 'normal'), {})])

    def test_configchannel_create_noargs_type_state(self, shell):
        """
        Test configchannel_create, interactive, testing "state" type.

        :param shell:
        :return:
        """
        puser = MagicMock(side_effect=[
            "John Smith", "config_channel", "Not ISO 9000 compliant", "state",
        ])
        with patch("spacecmd.configchannel.prompt_user", puser) as pmt:
            spacecmd.configchannel.do_configchannel_create(shell, "")

        assert puser.called
        assert shell.client.configchannel.create.called

        assert_args_expect(shell.client.configchannel.create.call_args_list,
                           [((shell.session, 'config_channel', 'John Smith',
                              'Not ISO 9000 compliant', 'state'), {})])

    def test_configchannel_create_noargs_wrong_type(self, shell):
        """
        Test configchannel_create, interactive, stop on wrong type

        :param shell:
        :return:
        """
        logger = MagicMock()
        puser = MagicMock(side_effect=[
            "John Smith", "config_channel", "Not ISO 9000 compliant", "sausage",
        ])
        with patch("spacecmd.configchannel.prompt_user", puser) as pmt, \
                patch("spacecmd.configchannel.logging", logger) as lgr:
            spacecmd.configchannel.do_configchannel_create(shell, "")

        assert not shell.client.configchannel.create.called
        assert puser.called
        assert logger.error.called
        assert_args_expect(logger.error.call_args_list,
                           [(('Only [normal/state] values are acceptable for type', ), {})])

    def test_configchannel_delete_noargs(self, shell):
        """
        Delete channel, no args.

        :param shell:
        :return:
        """

        logger = MagicMock()
        mprint = MagicMock()
        with patch("spacecmd.configchannel.logging", logger) as lgr, \
                patch("spacecmd.configchannel.print", mprint) as prt:
            spacecmd.configchannel.do_configchannel_delete(shell, "")

        assert not logger.error.called
        assert not shell.client.configchannel.deleteChannels.called
        assert not logger.debug.called
        assert not mprint.called
        assert not shell.do_configchannel_list.called
        assert shell.help_configchannel_delete.called

    def test_configchannel_delete_wrong_channel(self, shell):
        """
        Delete channel, missing channel

        :param shell:
        :return:
        """

        logger = MagicMock()
        mprint = MagicMock()
        shell.do_configchannel_list = MagicMock(return_value=[
            "base_channel"
        ])
        with patch("spacecmd.configchannel.logging", logger) as lgr, \
                patch("spacecmd.configchannel.print", mprint) as prt:
            spacecmd.configchannel.do_configchannel_delete(shell, "funny_channel")

        assert not mprint.called
        assert not shell.client.configchannel.deleteChannels.called
        assert not shell.help_configchannel_delete.called
        assert logger.error.called
        assert logger.debug.called

        assert_args_expect(logger.debug.call_args_list,
                           [(("configchannel_delete called with args ['funny_channel'], channels=[]", ), {})])
        assert_args_expect(logger.error.call_args_list,
                           [(('No channels matched argument(s): funny_channel', ), {})])

    def test_configchannel_delete(self, shell):
        """
        Test configchannel_delete

        :param shell:
        :return:
        """

        logger = MagicMock()
        mprint = MagicMock()
        shell.do_configchannel_list = MagicMock(return_value=[
            "base_channel"
        ])
        with patch("spacecmd.configchannel.logging", logger) as lgr, \
                patch("spacecmd.configchannel.print", mprint) as prt:
            spacecmd.configchannel.do_configchannel_delete(shell, "base*")

        assert not shell.help_configchannel_delete.called
        assert not logger.error.called
        assert mprint.called
        assert shell.client.configchannel.deleteChannels.called
        assert logger.debug.called

        assert_args_expect(logger.debug.call_args_list,
                           [(("configchannel_delete called with args ['base.*'], channels=['base_channel']", ), {})])
        assert_args_expect(shell.client.configchannel.deleteChannels.call_args_list,
                           [((shell.session, ['base_channel']), {})])