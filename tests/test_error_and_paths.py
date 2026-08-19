# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import tempfile
import unittest

PACKAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'src', 'harmony_hpack')
sys.path.insert(0, PACKAGE_DIR)

from utils import (format_cmd_error, interpret_will_pack_result,  # noqa: E402
                   missing_file_message, missing_modules_message,
                   require_existing_file, resolve_file_path,
                   resolve_hvigorw_command)


class FormatCmdErrorTest(unittest.TestCase):
    def test_includes_stderr_and_stdout(self):
        error = subprocess.CalledProcessError(
            1,
            ['python', 'hpack/PackFile.py', '--will'],
            output='stdout-from-packfile',
            stderr='ImportError: cannot import config on Linux'
        )
        message = format_cmd_error(error, "执行 willPack 失败")
        self.assertIn("执行 willPack 失败", message)
        self.assertIn("non-zero exit status 1", message)
        self.assertIn("ImportError: cannot import config on Linux", message)
        self.assertIn("stdout-from-packfile", message)

    def test_omits_empty_streams(self):
        error = subprocess.CalledProcessError(2, ['hvigorw'])
        message = format_cmd_error(error, "构建 Hap/Hsp 出错")
        self.assertIn("构建 Hap/Hsp 出错", message)
        self.assertNotIn("stderr:", message)
        self.assertNotIn("stdout:", message)

    def test_decodes_bytes_stderr(self):
        error = subprocess.CalledProcessError(
            1, ['java'], output=None, stderr=b'certificate not found'
        )
        message = format_cmd_error(error, "签名失败")
        self.assertIn("certificate not found", message)


class ResolveFilePathTest(unittest.TestCase):
    def test_absolute_posix_path_is_kept(self):
        self.assertEqual(resolve_file_path('/data/certs/release.cer', 'hpack'),
                         os.path.normpath('/data/certs/release.cer'))

    def test_relative_path_joins_base_dir(self):
        self.assertEqual(
            resolve_file_path(os.path.join('sign', 'release.cer'), 'hpack'),
            os.path.normpath(os.path.join('hpack', 'sign', 'release.cer'))
        )

    def test_linux_backslash_prefix_is_not_absolute(self):
        # Old code used startswith('/', '\\'), which treated \foo as absolute on Linux.
        resolved = resolve_file_path('\\windows-style.cer', 'hpack')
        if os.name != 'nt':
            self.assertFalse(os.path.isabs(resolved))
            self.assertTrue(resolved.startswith('hpack'))

    def test_expands_user_home(self):
        resolved = resolve_file_path('~/certs/app.cer', None)
        self.assertFalse(resolved.startswith('~'))
        self.assertIn('certs', resolved)

    def test_empty_path_returns_none(self):
        self.assertIsNone(resolve_file_path('', 'hpack'))
        self.assertIsNone(resolve_file_path(None, 'hpack'))


class RequireExistingFileTest(unittest.TestCase):
    def test_looked_in_message_when_missing(self):
        with self.assertRaises(Exception) as ctx:
            require_existing_file('missing.cer', '/tmp/hpack-sign-test', '证书 Cert')
        message = str(ctx.exception)
        self.assertIn('未找到证书 Cert', message)
        self.assertIn('已查找:', message)
        self.assertIn('missing.cer', message)

    def test_returns_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            cert = os.path.join(tmp, 'release.cer')
            with open(cert, 'w', encoding='utf-8') as f:
                f.write('dummy')
            self.assertEqual(
                require_existing_file('release.cer', tmp, '证书 Cert'),
                os.path.normpath(cert)
            )

    def test_unconfigured_path(self):
        with self.assertRaises(Exception) as ctx:
            require_existing_file('', 'hpack', 'Profile')
        self.assertIn('Profile 路径未配置', str(ctx.exception))

    def test_missing_file_message_uses_absolute_paths(self):
        message = missing_file_message('PackFile.py', 'hpack/PackFile.py')
        self.assertIn('未找到PackFile.py', message)
        self.assertIn(os.path.abspath('hpack/PackFile.py'), message)


class WillPackResultTest(unittest.TestCase):
    def test_success_returns_stdout(self):
        out, warning = interpret_will_pack_result(
            0, '{"data": "打包前传值"}', '', ['python', 'PackFile.py', '--will']
        )
        self.assertEqual(out, '{"data": "打包前传值"}')
        self.assertIsNone(warning)

    def test_exit_one_with_stdout_continues_and_keeps_stderr(self):
        out, warning = interpret_will_pack_result(
            1,
            '{"data": "打包前传值"}',
            'Exception ignored in: <_io.TextIOWrapper name=\'<stdout>\'>',
            ['python', 'hpack/PackFile.py', '--will']
        )
        self.assertEqual(out, '{"data": "打包前传值"}')
        self.assertIn('退出码 1', warning)
        self.assertIn('TextIOWrapper', warning)

    def test_exit_one_without_stdout_raises_with_stderr(self):
        with self.assertRaises(Exception) as ctx:
            interpret_will_pack_result(
                1,
                '',
                'Traceback: from config import Config failed',
                ['/data/py_env/xxx/bin/python', 'hpack/PackFile.py', '--will']
            )
        message = str(ctx.exception)
        self.assertIn('执行 willPack 失败', message)
        self.assertIn('from config import Config failed', message)
        self.assertIn('hpack/PackFile.py', message)


class MissingModulesMessageTest(unittest.TestCase):
    def test_missing_build_dir(self):
        path = os.path.join(tempfile.gettempdir(), 'hpack-no-such-build-dir')
        message = missing_modules_message(path)
        self.assertIn('构建目录不存在', message)
        self.assertIn('已查找:', message)
        self.assertIn(os.path.abspath(path), message)
        self.assertNotIn('请检查你的签名文件配置', message)

    def test_empty_build_dir_does_not_blame_certs_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            message = missing_modules_message(tmp)
            self.assertIn('未找到 .hap/.hsp 文件', message)
            self.assertIn(os.path.abspath(tmp), message)
            self.assertIn('willPack / hvigorw', message)
            self.assertNotIn('请检查你的签名文件配置', message)


class HvigorwLookupTest(unittest.TestCase):
    def test_looked_in_cwd_when_not_on_path(self):
        original = os.environ.get('PATH')
        try:
            os.environ['PATH'] = ''
            with tempfile.TemporaryDirectory() as tmp:
                cwd = os.getcwd()
                os.chdir(tmp)
                try:
                    with self.assertRaises(Exception) as ctx:
                        resolve_hvigorw_command()
                finally:
                    os.chdir(cwd)
            message = str(ctx.exception)
            self.assertIn('未找到hvigorw', message)
            self.assertIn('已查找:', message)
            self.assertIn('hvigorw', message)
        finally:
            if original is None:
                os.environ.pop('PATH', None)
            else:
                os.environ['PATH'] = original

    def test_uses_project_root_hvigorw_when_not_on_path(self):
        original = os.environ.get('PATH')
        try:
            os.environ['PATH'] = ''
            with tempfile.TemporaryDirectory() as tmp:
                script = os.path.join(tmp, 'hvigorw')
                with open(script, 'w', encoding='utf-8') as f:
                    f.write('#!/bin/sh\n')
                os.chmod(script, 0o755)
                cwd = os.getcwd()
                os.chdir(tmp)
                try:
                    found = resolve_hvigorw_command()
                finally:
                    os.chdir(cwd)
            self.assertEqual(os.path.abspath(found), os.path.abspath(script))
        finally:
            if original is None:
                os.environ.pop('PATH', None)
            else:
                os.environ['PATH'] = original


if __name__ == '__main__':
    unittest.main()
