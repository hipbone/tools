#!/usr/bin/env python3
"""
YAML to JSON converter script
"""
import json
import yaml
import argparse
import sys
from pathlib import Path


def convert_yaml_to_json(yaml_file, json_file=None, indent=2):
    """
    Convert YAML file to JSON file

    Args:
        yaml_file: Path to input YAML file
        json_file: Path to output JSON file (optional)
        indent: JSON indentation level (default: 2)
    """
    try:
        # Read YAML file
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Determine output file path
        if json_file is None:
            json_file = Path(yaml_file).with_suffix('.json')

        # Write JSON file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

        print(f"Successfully converted: {yaml_file} -> {json_file}")
        return True

    except FileNotFoundError:
        print(f"Error: File not found - {yaml_file}", file=sys.stderr)
        return False
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML format - {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Convert YAML file to JSON format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.yaml
  %(prog)s input.yaml -o output.json
  %(prog)s input.yaml --indent 4
        """
    )

    parser.add_argument('yaml_file', help='Input YAML file path')
    parser.add_argument('-o', '--output', dest='json_file',
                        help='Output JSON file path (default: same name with .json extension)')
    parser.add_argument('-i', '--indent', type=int, default=2,
                        help='JSON indentation level (default: 2)')

    args = parser.parse_args()

    success = convert_yaml_to_json(args.yaml_file, args.json_file, args.indent)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
