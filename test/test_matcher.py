#
# SPDX-FileCopyrightText: 2017-now, See `CONTRIBUTORS.lst`
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import Final

import pytest

pytest_plugins = ['pytester']

@pytest.fixture()
def ourtestdir(pytester: pytest.Pytester) -> pytest.Pytester:
    # Write a sample config file
    pytester.makefile(
        '.ini'
      , pytest=f"""
            [pytest]
            addopts = -vv -ra
            pm-patterns-base-dir = {pytester.path!s}
        """
      )
    return pytester


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


def simple_test(ourtestdir) -> None:
    # Write a sample expectations file
    ourtestdir.makefile('.out', test_sample_out='Hello Africa!')
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


def failed_test(ourtestdir) -> None:
    # Write a sample expectations file
    ourtestdir.makefile('.out', test_not_matched='Hello Africa!')
    # Write a sample test
    ourtestdir.makepyfile("""
        def test_not_matched(capfd, expected_out):
            print('Unexpected output')
            stdout, stderr = capfd.readouterr()
            assert expected_out == stdout
      """
    )

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


def regex_match_test(ourtestdir) -> None:
    # Write a sample expectations file
    ourtestdir.makefile('.out', test_sample_out='.*Africa!\nHello\\s+.*!\n')
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


def regex_fail_match_test(ourtestdir) -> None:
    # Write a sample expectations file
    ourtestdir.makefile('.out', test_sample_out='.*Africa!\nEhlo\\s+.*!\n')
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


def yaml_match_test(ourtestdir) -> None:
    # Write a sample result and expected file
    ourtestdir.makefile(
        '.yaml'
      , expected_yaml="""
        some-key: some-value
        another-key: another-value
        simple-array:
            - satu
            - dua
            - tiga
        """
      )
    ourtestdir.makefile(
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


def yaml_match_failure_test(ourtestdir) -> None:
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
    ourtestdir.makefile(
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


def parametrized_case_test(ourtestdir) -> None:
    # Given testing argvalues and expected decorations
    testing_pairs = [
        ((0, 'y'), '[0-y]'),
        ((1, 'some words'), '[1-some%20words]'),
        ((2, '~/some/path/'), '[2-~%2Fsome%2Fpath%2F]'),
    ]
    # Write sample expectation files
    for values, decoration in testing_pairs:
        (ourtestdir.path / f'test_parametrized{decoration}.out').write_text(str(values) + '\n')

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
    result.assert_outcomes(passed=3)


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
        (ourtestdir.path / p).write_text('')

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
