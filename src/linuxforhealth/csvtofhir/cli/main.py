import argparse
import sys
from typing import List

from linuxforhealth.csvtofhir.cli.convert import convert_to_fhir
from linuxforhealth.csvtofhir.cli.validate import validate_data_contract

CLI_DESCRIPTION = """
CSVToFHIR converts custom delimited records to FHIR Resources (JSON).
The CLI supports:
- DataContract Validation
- Source Record Conversion
"""


def create_arg_parser():
    """
    Creates argument parsers for the following programs/sub-parsers:
    - validation
    - convert
    :return: The argument parser
    """
    arg_parser = argparse.ArgumentParser(
        prog="CSV To FHIR",
        description=CLI_DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter
    )

    sub_parsers = arg_parser.add_subparsers()

    # validate
    validate = sub_parsers.add_parser("validate", help="Validate a CSVToFHIR DataContract")
    validate.add_argument("-f",
                          help="The path to the DataContract configuration file")
    validate.set_defaults(func=validate_data_contract)

    # fixture
    convert = sub_parsers.add_parser("convert", help="Convert source records to FHIR")

    input_group = convert.add_mutually_exclusive_group()
    input_group.add_argument("-d", help="Specifies the base processing directory for directory mode.")
    input_group.add_argument("-f", help="Specifies the single file to process for file mode.")

    convert.add_argument("-c",
                         default=None,
                         help="The config directory location. Required if -f is used.",
                         required=False)

    convert.add_argument("-o", help="The Fixture Output Directory", required=False)

    convert.set_defaults(func=convert_to_fhir)

    return arg_parser


def main(received_arguments: List[str] = None):
    """
    Executes the CLI utility
    :param received_arguments: The arguments from the CLI. Defaults to None
    """
    parser = create_arg_parser()
    args = parser.parse_args(received_arguments)

    if hasattr(args, "func"):

        if "convert" in args.func.__name__:
            # validate convert file mode args
            file_arg = getattr(args, "f", None)
            config_arg = getattr(args, "c", None)
            if file_arg and not config_arg:
                # parser error exits the CLI
                parser.error("-c is required when -f is used")

        # execute CLI
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    # parsing system arguments and passing them in so that we can:
    # - bootstrap test cases easily
    # - print help information if no arguments are provided
    system_arguments = sys.argv[1:] if sys.argv else []
    main(system_arguments)
