#!/usr/bin/env python
# SPDX-FileCopyrightText: 2024-now, Alex Turbov <zaufi@pm.me>
# SPDX-License-Identifier: CC0-1.0

"""Print any key from TOML file."""

import argparse
import functools
import hashlib
import json
import sys

try:
  import tomllib
except ImportError:
  import tomli as tomllib


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Access nested data of a TOML file using dot-separated keys.'
      )
    parser.add_argument(
        '--file-path'
      , type=str
      , default='pyproject.toml', help='Path to the TOML file'
      )
    parser.add_argument(
        'keys'
      , type=str
      , help='Dot-separated keys to access nested data'
      )
    parser.add_argument(
        '--hash'
      , action='store_true'
      , help='Print the SHA-1 hash of the found value instead of plain output'
      )
    parser.add_argument(
        '--json'
      , action='store_true'
      , help='Print the value as JSON'
      )

    args = parser.parse_args()

    with open(args.file_path, 'rb') as fd:
        data = tomllib.load(fd)

    try:
        selected_key = functools.reduce(
            lambda state, part: state[part]
          , args.keys.split('.')
          , data
          )
        if args.json:
          result = json.dumps(selected_key, indent=2)
        else:
          match selected_key:
            case str():
              result = selected_key
            case list():
              if all(isinstance(v, str) for v in selected_key):
                result = '\n'.join(selected_key)
              else:
                # TODO Don't care for now!
                msg = 'Some items of the selected key are not strings'
                raise TypeError(msg)
            case _:
              print(f"Error: Dunno how to print key '{args.keys}' of type {type(selected_key).__name__}.")
              sys.exit(1)

        if args.hash:
            print(hashlib.sha1(str(result).encode()).hexdigest())
        else:
            print(result)

    except TypeError as e:
        print(f'Error: {e}.')
        sys.exit(1)

    except KeyError as e:
        print(f"Error: Given key {e} not found in the '{args.file_path}'.")
        sys.exit(1)

if __name__ == '__main__':
    main()
