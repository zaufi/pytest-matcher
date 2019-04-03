# -*- coding: utf-8 -*-
#
# Copyright (c) 2017-2018 Alex Turbov <i.zaufi@gmail.com>
#
# Pytest-match plugin is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pytest-match plugin is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest

pytest_plugins = ['pytester']

@pytest.fixture
def ourtestdir(testdir):
    # Write a sample config file
    testdir.tmpdir.join('pytest.ini').write(
        '[pytest]\n'
        'addopts = -ra\n'
        'pm-patterns-base-dir = {}'.format(str(testdir.tmpdir))
      )
    yield testdir


def no_file_test(ourtestdir):
    # Create a temporary pytest test file
    ourtestdir.makepyfile('''
        def test_no_expected_file(capfd, expected_out):
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
    ''')

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(skipped=1)
    result.stdout.re_match_lines([
        '.*Pattern file not found .*test_no_expected_file.out`'
      ])


def simple_test(ourtestdir):
    # Write a sample expectations file
    ourtestdir.tmpdir.join('test_sample_out.out').write('Hello Africa!\n')
    # Write a sample test (finally)
    ourtestdir.makepyfile('''
        def test_sample_out(capfd, expected_out):
            print('Hello Africa!')
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
    ''')

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(passed=1)


def failed_test(ourtestdir):
    # Write a sample expectations file
    ourtestdir.tmpdir.join('test_not_matched.out').write('Hello Africa!')
    # Write a sample test (finally)
    ourtestdir.makepyfile('''
        def test_not_matched(capfd, expected_out):
            print('Unexpected output')
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
    ''')

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        'E         ---[BEGIN actual output]---'
      , 'E         Unexpected output'
      , 'E         ---[END actual output]---'
      , 'E         ---[BEGIN expected output]---'
      , 'E         Hello Africa!'
      , 'E         ---[END expected output]---'
      ])


def result_yaml_not_found_test(ourtestdir):
    # Write a sample test (finally)
    ourtestdir.makepyfile('''
        import pathlib
        def test_yaml(capfd, expected_yaml):
            assert expected_yaml == pathlib.Path('result.yaml')
    ''')
    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(skipped=1)
    result.stdout.re_match_lines([
        '.*Result YAML file not found `result.yaml`'
      ])


def expected_yaml_not_found_test(ourtestdir):
    # Write a sample result file
    ourtestdir.makefile(
        '.yaml'
      , result='''
        some-key: some-value
        another-key: another-value
        simple-array:
            - satu
            - dua
            - tiga
    ''')
    # Write a sample test (finally)
    ourtestdir.makepyfile('''
        import pathlib
        def test_yaml(capfd, expected_yaml):
            assert expected_yaml == pathlib.Path('result.yaml')
    ''')
    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(skipped=1)
    result.stdout.re_match_lines([
        '.*Expected YAML file not found `.*test_yaml.yaml`'
      ])


def yaml_match_test(ourtestdir):
    # Write a sample result and expected file
    ourtestdir.makefile(
        '.yaml'
      , expected_yaml='''
        some-key: some-value
        another-key: another-value
        simple-array:
            - satu
            - dua
            - tiga
    ''')
    ourtestdir.makefile(
        '.yaml'
      , test_yaml='''
        another-key: another-value
        simple-array:
            - satu
            - dua
            - tiga
        some-key: some-value
    ''')
    # Write a sample test (finally)
    ourtestdir.makepyfile('''
        import pathlib
        def test_yaml(capfd, expected_yaml):
            assert expected_yaml == pathlib.Path('test_yaml.yaml')
    ''')
    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(passed=1)


def yaml_match_failure_test(ourtestdir):
    # Write a sample result and expected file
    ourtestdir.makefile(
        '.yaml'
      , result='''
        some-key: some-value
        another-key: another-value
        simple-array:
            - satu
            - dua
            - tiga
    ''')
    ourtestdir.makefile(
        '.yaml'
      , test_yaml='''
        another-key: another-value
        simple-array:
            - dua
            - tiga
            - satu
    ''')
    # Write a sample test (finally)
    ourtestdir.makepyfile('''
        import pathlib
        def test_yaml(capfd, expected_yaml):
            assert expected_yaml == pathlib.Path('result.yaml')
    ''')

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        'E         ---[BEGIN actual result]---'
      , 'E         ---[END actual result]---'
      , 'E         ---[BEGIN expected result]---'
      , 'E         ---[END expected result]---'
      ])
