#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

# Standard imports
import platform
from typing import Final

# Third party packages
import pytest


def no_file_test(ourtestdir) -> None:
    # Create a temporary pytest test file
    ourtestdir.makepyfile("""
        def test_no_expected_file(capfd, expected_out):
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
        """
      )

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(skipped=1)
    result.stdout.re_match_lines([
        '.*Pattern file not found .*test_no_expected_file.out`'
      ])


def simple_test(ourtestdir, expectdir) -> None:
    # Write a sample expectations file
    expectdir.makepatternfile('.out', test_sample_out='Hello Africa!')
    # Write a sample test
    ourtestdir.makepyfile("""
        def test_sample_out(capfd, expected_out):
            print('Hello Africa!', end='')
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
            assert stderr == ''
        """
      )

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize('eol', [r'\r', r'\n', r'\r\n'])
def failed_test(eol, ourtestdir, expectdir) -> None:
    # Write a sample expectations file
    expectdir.makepatternfile('.out', test_not_matched='Hello Africa!')
    # Write a sample test
    ourtestdir.makepyfile(f"""
        def test_not_matched(capfd, expected_out):
            print('Unexpected output', end='{eol}')
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
        """
    )

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        'E         ---[BEGIN actual output]---'
      , 'E         Unexpected output↵'
      , 'E         ---[END actual output]---'
      , 'E         ---[BEGIN expected output]---'
      , 'E         Hello Africa!'
      , 'E         ---[END expected output]---'
      ])


def regex_match_test(ourtestdir, expectdir) -> None:
    # Write a sample expectations file
    expectdir.makepatternfile('.out', test_sample_out='.*Africa!\nHello\\s+.*!\n')
    # Write a sample test
    ourtestdir.makepyfile("""
        def test_sample_out(capfd, expected_out):
            print('Hello Africa!')
            print('Hello Asia!')
            stdout, stderr = capfd.readouterr()
            assert expected_out.match(stdout) == True
            assert stderr == ''
        """
      )

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(passed=1)


def regex_fail_match_test(ourtestdir, expectdir) -> None:
    # Write a sample expectations file
    expectdir.makepatternfile('.out', test_sample_out='.*Africa!\nEhlo\\s+.*!\n')
    # Write a sample test (finally)
    ourtestdir.makepyfile("""
        def test_sample_out(capfd, expected_out):
            print('Hello Africa!')
            print('Hello Asia!')
            stdout, stderr = capfd.readouterr()
            assert expected_out.match(stdout) == True
            assert stderr == ''
        """
      )

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines([
        ".*The test output doesn't match to the expected regex"
      ])


def result_yaml_not_found_test(ourtestdir) -> None:
    # Write a sample test
    ourtestdir.makepyfile("""
        import pathlib
        def test_yaml(capfd, expected_yaml):
            assert expected_yaml == pathlib.Path('result.yaml')
        """
      )
    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(skipped=1)
    result.stdout.re_match_lines(['.*Result YAML file not found `result.yaml`'])


def expected_yaml_not_found_test(ourtestdir) -> None:
    # Write a sample result file
    ourtestdir.makefile(
        '.yaml'
      , result="""
        some-key: some-value
        another-key: another-value
        simple-array:
          - satu
          - dua
          - tiga
        """
      )
    # Write a sample test
    ourtestdir.makepyfile("""
        import pathlib
        def test_yaml(capfd, expected_yaml):
            assert expected_yaml == pathlib.Path('result.yaml')
        """
      )
    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(skipped=1)
    result.stdout.re_match_lines([
        '.*Expected YAML file not found `.*test_yaml.yaml`'
      ])


def yaml_match_test(ourtestdir, expectdir) -> None:
    # Write a sample result and expected file
    ourtestdir.makefile(
        '.yaml'
      , test_yaml="""
        some-key: some-value
        another-key: another-value
        simple-array:
          - satu
          - dua
          - tiga
        """
      )
    expectdir.makepatternfile(
        '.yaml'
      , test_yaml="""
        another-key: another-value
        simple-array:
          - satu
          - dua
          - tiga
        some-key: some-value
        """
      )
    # Write a sample test
    ourtestdir.makepyfile("""
        import pathlib
        def test_yaml(capfd, expected_yaml):
            assert expected_yaml == pathlib.Path('test_yaml.yaml')
        """
      )
    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(passed=1)


def yaml_match_failure_test(ourtestdir, expectdir) -> None:
    # Write a sample result and expected file
    ourtestdir.makefile(
        '.yaml'
      , result="""
        some-key: some-value
        another-key: another-value
        simple-array:
          - satu
          - dua
          - tiga
        """
      )
    expectdir.makepatternfile(
        '.yaml'
      , test_yaml="""
        another-key: another-value
        simple-array:
          - dua
          - tiga
          - satu
        """
      )
    # Write a sample test
    ourtestdir.makepyfile("""
        import pathlib
        def test_yaml(capfd, expected_yaml):
            assert expected_yaml == pathlib.Path('result.yaml')
        """
      )

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        'E         ---[BEGIN actual result]---'
      , 'E         ---[END actual result]---'
      , 'E         ---[BEGIN expected result]---'
      , 'E         ---[END expected result]---'
      ])


def parametrized_case_test(ourtestdir, expectdir) -> None:
    # Given testing argvalues and expected decorations
    testing_pairs = [
        ((0, 'y'), '[0-y]')
      , ((1, 'some words'), '[1-some%20words]')
      , ((2, '~/some/path/'), '[2-~%2Fsome%2Fpath%2F]')
      , ((3, 'with.dot'), '[3-with.dot]')
      ]
    # Write sample expectation files
    for values, decoration in testing_pairs:
        (expectdir.path / f'test_parametrized{decoration}.out').write_text(str(values) + '\n')

    # Write a sample test
    ourtestdir.makepyfile(f"""
        import pytest
        @pytest.mark.parametrize('x,y', {[p[0] for p in testing_pairs]})
        def test_parametrized(x, y, capfd, expected_out):
            print((x, y))
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
            assert stderr == ''
        """
      )

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(passed=len(testing_pairs))


@pytest.mark.parametrize(('return_codes', 'expected_code'), [(False, 0), (True, 1)])
def reveal_unused_files_test(return_codes, expected_code, ourtestdir, monkeypatch) -> None:
    # Write sample expectation files
    (ourtestdir.path / 'TestClass').mkdir()
    paths: Final[list[str]] = [
        'test_a.out'
      , 'test_a.out.bak'
      , 'TestClass/test_a.out'
        # Write some unused files
      , 'test_a.err'
      , 'test_b.out'
      ]
    for p in paths:
        (ourtestdir.path / p).touch()

    # Write a sample test
    ourtestdir.makepyfile("""
        def test_a(expected_out): pass
        class TestClass:
            def test_a(self, expected_out): pass
        """
      )

    # Run all tests with pytest
    if return_codes:
        monkeypatch.setenv('PYTEST_MATCHER_RETURN_CODES', 'yes')

    result = ourtestdir.runpytest('--pm-reveal-unused-files')
    assert result.ret == expected_code
    result.stdout.fnmatch_lines([
        f'{(ourtestdir.path / p)!s}'
        for p in ('test_a.err', 'test_b.out')
      ])


@pytest.mark.parametrize(
    ('fmt', 'file_name', 'cls_name', 'expected_path')
  , [
        # Format w/ just a function name produces an expectation file in the base dir
        ('{fn}',                 'simple_test',     None,      'test_fn.out')
        # Any leading `/` doesn't produce any files in the FS root
      , ('/{fn}',                'simple_test',     None,      'test_fn.out')
        # Any trailing slashes also ignored
      , ('{fn}/',                'simple_test',     None,      'test_fn.out')
        # Play w/ other components...
      , ('{module}-{fn}',        'simple_test',     None,      'simple_test-test_fn.out')
      , ('{module}/{fn}',        'subdir_test',     None,      'subdir_test/test_fn.out')
        # ... patterns may include some static text
      , ('py-{module}/exp-{fn}', 'pfx_subdir_test', None,      'py-pfx_subdir_test/exp-test_fn.out')
        # Missed class name means no corresponding subdir
      , ('{class}/{fn}',         'subdir_test',     None,      'test_fn.out')
        # Missed class name in the format is Ok
      , ('{fn}',                 'simple_test',     'TestCls', 'test_fn.out')
        # Play w/ other components...
      , ('{class}+{fn}',         'simple_test',     'TestCls', 'TestCls+test_fn.out')
      , ('{module}/{class}/{fn}','simple_test',     'TestCls', 'simple_test/TestCls/test_fn.out')
        # Redundant '/' just ignored
      , ('{module}//{class}//{fn}','simple_test',   'TestCls', 'simple_test/TestCls/test_fn.out')
        # '.' is meaningless
      , ('./{class}/{fn}',         'simple_test',   'TestCls', 'TestCls/test_fn.out')
      , ('{class}/./{fn}',         'simple_test',   'TestCls', 'TestCls/test_fn.out')
    ]
  )
def fn_fmt_test(pytester: pytest.Pytester, fmt, file_name, cls_name, expected_path) -> None:
    # Write a sample config file
    pytester.makefile(
        '.ini'
      , pytest=f"""
            [pytest]
            addopts = -vv -ra
            pm-patterns-base-dir = .
            pm-pattern-file-fmt = {fmt}
        """
      )

    # Write a sample expectations file
    path = pytester.path / expected_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('Hello Africa!')

    # Write a sample test
    indent = ' ' * (4 if cls_name is not None else 0)
    kwargs = {file_name: f"""
        {('class ' + cls_name + ':') if cls_name is not None else ''}
        {indent}def test_fn({'self, ' if cls_name is not None else ''}capfd, expected_out):
        {indent}    print('Hello Africa!', end='')
        {indent}    stdout, stderr = capfd.readouterr()
        {indent}    assert expected_out == stdout
        {indent}    assert stderr == ''
        """
      }
    pytester.makepyfile(**kwargs)

    # Run all tests with pytest
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def pm_pattern_file_fmt_directory_traversal_test(pytester: pytest.Pytester) -> None:
    # Write a sample config file
    pytester.makefile(
        '.ini'
      , pytest="""
            [pytest]
            addopts = -vv -ra
            pm-patterns-base-dir = .
            pm-pattern-file-fmt = ../{{class}}/../{{fn}}
        """
      )
    # Run all tests with pytest
    result = pytester.runpytest()
    result.stderr.re_match_lines([
        'ERROR: Directory traversal is not allowed for `pm-pattern-file-fmt` or `pm-patterns-base-dir` option'
      ])


@pytest.mark.parametrize(
    ('sfx', 'filename')
  , [
        # No args marker
        ('', f'test_sfx-{platform.system()}.out')
        # Positional arg marker
      , ('platform.system()', f'test_sfx-{platform.system()}.out')
      , ('"with.dot"', 'test_sfx-with.dot.out')
        # Positional args marker
      , (
            '"py", f"{sys.version_info.major}", platform.system()'
          , f'test_sfx-py-3-{platform.system()}.out'
        )
        # KW arg marker
      , ('suffix=platform.system()', f'test_sfx-{platform.system()}.out')
        # Positional and KW args marker
      , (
            '"py", f"{sys.version_info.major}", suffix=platform.system()'
          , f'test_sfx-py-3-{platform.system()}.out'
        )
        # URL-escape has applied
      , ('"[%&()*+/]"', 'test_sfx-[%25%26%28%29%2A%2B%2F].out')
    ]
  )
def suffix_test(pytester, sfx, filename) -> None:
    # Write a sample config file
    pytester.makefile(
        '.ini'
      , pytest="""
            [pytest]
            addopts = -vv -ra
            pm-patterns-base-dir = .
            pm-pattern-file-fmt = {fn}{suffix}
        """
      )

    # Write a sample expectations file
    (pytester.path / filename).write_text('Hello Africa!\n')

    # Write a sample test
    pytester.makepyfile(f"""
        import platform
        import pytest
        import sys

        @pytest.mark.expect_suffix({sfx})
        def test_sfx(capfd, expected_out):
            print('Hello Africa!')
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
            assert stderr == ''
        """
      )

    # Run all tests with pytest
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
