#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

# Standard imports
import pathlib
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
        ".*The test output doesn't match the expected regex."
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


@pytest.mark.parametrize(
    ('fmt', 'error_string')
  , [
        pytest.param(
            '{unknown}'
          , "'pm-pattern-file-fmt' has invalid placeholder: 'unknown'"
          , id='invalid-placeholders-1'
          )
      , pytest.param(
            '{fn}/{unknown}/{class}'
          , "'pm-pattern-file-fmt' has invalid placeholder: 'unknown'"
          , id='invalid-placeholders-2'
          )
      , pytest.param(
            '{satu}-{dua}'
          , "'pm-pattern-file-fmt' has invalid placeholders: 'satu', 'dua'"
          , id='invalid-placeholders-3'
          )
      , pytest.param(
            '{fn'
          , "'pm-pattern-file-fmt' has incorrect format: expected '}' before end of string"
          , id='placeholder-syntax-error-1'
          )
      , pytest.param(
            'fn}'
          , "'pm-pattern-file-fmt' has incorrect format: single '}' encountered in format string"
          , id='placeholder-syntax-error-2'
          )
      , pytest.param(
            'static string'
          , "'pm-pattern-file-fmt' should have at least one placeholder"
          , id='missed-placeholder'
          )
      , pytest.param(
            '../{class}/../{fn}'
          , 'Directory traversal is not allowed for `pm-pattern-file-fmt` or `pm-patterns-base-dir` option'
          , id='directory-traversal'
          )
    ]
  )
def pm_pattern_file_bad_fmt_test(pytester: pytest.Pytester, fmt, error_string) -> None:
    # Write a sample bad config file
    pytester.makefile(
        '.ini'
      , pytest=f"""
            [pytest]
            pm-pattern-file-fmt = {fmt}
        """
      )
    # Run all tests with pytest
    result = pytester.runpytest()
    result.stderr.re_match_lines([f'ERROR: {error_string}'])


@pytest.mark.parametrize(
    ('sfx', 'filename')
  , [
        pytest.param('', f'test_sfx-{platform.system()}.out', id='no-args-marker')
      , pytest.param(
            'platform.system()'
          , f'test_sfx-{platform.system()}.out'
          , id='positional-arg-marker-1'
          )
      , pytest.param(
            '"with.dot"'
          , 'test_sfx-with.dot.out'
          , id='positional-arg-marker-2'
          )
      , pytest.param(
            '"py", f"{sys.version_info.major}", platform.system()'
          , f'test_sfx-py-3-{platform.system()}.out'
          , id='positional-arg-marker-3'
          )
      , pytest.param(
            'suffix=platform.system()'
          , f'test_sfx-{platform.system()}.out'
          , id='kw-arg-marker-1'
          )
      , pytest.param(
            '"py", f"{sys.version_info.major}", suffix=platform.system()'
          , f'test_sfx-py-3-{platform.system()}.out'
          , id='positional-and-kw-args-marker'
          )
      , pytest.param(
            '"[%&()*+/]"'
          , 'test_sfx-[%25%26%28%29%2A%2B%2F].out'
          , id='url-escape-applied'
          )
    ]
  )
@pytest.mark.pytest_ini_options(pm_pattern_file_fmt='{fn}{suffix}')
def suffix_test(ourtestdir, sfx, filename) -> None:
    # Write a sample expectations file
    (ourtestdir.path / filename).write_text('Hello Africa!\n')

    # Write a sample test
    ourtestdir.makepyfile(f"""
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
    result = ourtestdir.runpytest()
    result.assert_outcomes(passed=1)


@pytest.mark.pytest_ini_options(pm_pattern_file_fmt='{fn}', pm_mismatch_style='diff')
def diff_test(ourtestdir) -> None:
    # Write a sample expectations file
    (ourtestdir.path / 'test_diff.out').write_text('Hello Africa!\n')

    # Write a sample test that will fail
    ourtestdir.makepyfile("""
        import platform
        import pytest
        import sys

        def test_diff(capfd, expected_out):
            print('Hello America!')
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
            assert stderr == ''
        """
      )

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        'E         ---[BEGIN expected vs actual diff]---'
      , 'E         --- expected'
      , 'E         +++ actual'
      , 'E         @@ -1 +1 @@'
      , 'E         -Hello Africa!↵'
      , 'E         +Hello America!↵'
      , 'E         ---[END expected vs actual diff]---'
      ])


@pytest.mark.parametrize(
    ('on_store_params', 'error_string')
  , [
        pytest.param(
            'drop_head="string"'
          , "parameter with invalid type: 'drop_head'"
          , id='invalid-drop_head-type'
          )
      , pytest.param(
            'drop_head=-1'
          , "invalid value `-1` for parameter 'drop_head'"
          , id='invalid-drop_head-value'
          )
      , pytest.param(
            'drop_head="string", drop_tail="string"'
          , "parameters with invalid type: 'drop_head', 'drop_tail'"
          , id='invalid-drop-types'
          )
      , pytest.param(
            'replace_matched_lines=["[*"]'
          , "invalid regular expression: '[*'"
          , id='invalid-regex'
          )
    ]
  )
@pytest.mark.pytest_ini_options(pm_pattern_file_fmt='{fn}')
def bad_on_store_marker_test(ourtestdir, on_store_params: str, error_string: str) -> None:
    # Write a sample test
    ourtestdir.makepyfile(f"""
        import pytest

        @pytest.mark.on_store({on_store_params})
        def test_bad_on_store_marker(expected_out):
            pass
        """
      )

    # On first run store the patched pattern...
    result = ourtestdir.runpytest('--pm-save-patterns')
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines([
        f"E           _pytest.config.exceptions.UsageError: 'on_store' marker got {error_string}"
      ])


HELLO_STRING: Final[str] = 'Hello Africa!\\nHola Antarctica!\\nHello Americas!'

@pytest.mark.parametrize(
    ('on_store_params', 'test_string', 'second_run')
  , [
        pytest.param('drop_head=1', HELLO_STRING, False, id='drop_head_1')
      , pytest.param('drop_head=2', HELLO_STRING, False, id='drop_head_2')
      , pytest.param('drop_tail=1', HELLO_STRING, False, id='drop_tail_1')
      , pytest.param('drop_tail=2', HELLO_STRING, False, id='drop_tail_2')
      , pytest.param(
            'drop_head=1, drop_tail=1'
          , HELLO_STRING
          , False
          , id='drop_head_and_tail_1'
        )
      , pytest.param(
            "replace_matched_lines=['Hello .*!']"
          , HELLO_STRING
          , True
          , id='replace_matched_lines'
        )
      , pytest.param(
            "drop_head=1, replace_matched_lines=['Hola .*!'], drop_tail=1"
          , HELLO_STRING
          , True
          , id='replace_matched_lines_and_drops'
        )
      , pytest.param(
            "replace_matched_lines=['Hola .*!']"
          , 'Hello ++ Africa!\\nHola Antarctica!\\nHello * Americas!'
          , True
          , id='need_escape_regex_chars'
        )
    ]
  )
@pytest.mark.pytest_ini_options(pm_pattern_file_fmt='{fn}')
def on_store_marker_test(
    ourtestdir
  , on_store_params: str
  , test_string: str
  , second_run: bool                                        # NOQA: FBT001
  , expected_out
  ) -> None:
    # Write a sample test
    ourtestdir.makepyfile(f"""
        import pytest

        @pytest.mark.on_store({on_store_params})
        def test_on_store_marker(capfd, expected_out):
            print('{test_string!s}')
            stdout, _ = capfd.readouterr()
            assert expected_out.match(stdout) == True
        """
      )

    # On first run store the patched pattern...
    result = ourtestdir.runpytest('--pm-save-patterns')
    result.assert_outcomes(skipped=1)

    # Check the stored pattern
    stored_pattern = pathlib.Path.cwd() / 'test_on_store_marker.out'
    assert stored_pattern.exists()
    actual_pattern = stored_pattern.read_text()
    assert actual_pattern == expected_out

    # Second run should pass!
    if second_run:
        result = ourtestdir.runpytest()
        result.assert_outcomes(passed=1)


@pytest.mark.pytest_ini_options(pm_pattern_file_fmt='{fn}')
def printable_test(ourtestdir) -> None:
    # Write a sample expectations file
    ourtestdir.makefile('.out', test_printing='Hello Africa!')

    # Write a sample test
    ourtestdir.makepyfile("""
        def test_printing(expected_out):
            print(f'printable_test: expected_out="{expected_out}"')
            assert False
        """
      )

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(failed=1)

    result.stdout.fnmatch_lines([
        'printable_test: expected_out="Hello Africa!"'
      ])


@pytest.mark.pytest_ini_options(pm_pattern_file_fmt='{fn}')
def repr_test(ourtestdir) -> None:
    # Write a sample expectations file
    ourtestdir.makefile('.out', test_repr='Hello Africa!')

    # Write a sample test
    ourtestdir.makepyfile("""
        def test_repr(expected_out):
            print(f'repr_test: {expected_out=}')
            assert False
        """
      )

    # Run all tests with pytest
    result = ourtestdir.runpytest()
    result.assert_outcomes(failed=1)

    result.stdout.re_match_lines([
        "repr_test: expected_out=\\(pattern_filename='.*/test_repr.out', pattern='Hello Africa!'\\)"
      ])
