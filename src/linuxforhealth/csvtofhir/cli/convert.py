import json
import os
import re
from collections import defaultdict
from json import JSONDecodeError
from typing import Dict, List

from linuxforhealth.csvtofhir.converter import convert
from linuxforhealth.csvtofhir.model.contract import DataContract, load_data_contract
from linuxforhealth.csvtofhir.support import validate_paths


def _filter_input_files(input_files: List[str], config_dir: str) -> List[str]:
    """
    Filters an input file list using the file definitions in a data contract.
    Files which do not contain any data contract file definition key are removed.

    :param input_files: The input files to process
    :param config_dir: The configuration directory path
    :return: list of filtered files
    """
    data_contract_path = os.path.join(config_dir, "data-contract.json")
    data_contract: DataContract = load_data_contract(data_contract_path)
    file_definition_names: List[str] = [f.lower() for f in data_contract.fileDefinitions.keys()]

    filtered_files: List[str] = []
    for f in input_files:
        base_file_name = os.path.splitext(os.path.basename(f))[0]
        # match the data-contract key to any fragment of the file name
        for def_name in file_definition_names:
            if def_name.lower() in base_file_name.lower():
                if f not in filtered_files:
                    filtered_files.append(f)

    filtered_files.sort()
    return filtered_files


def _convert_single_file(file_path: str, config_dir_path: str, output_dir_path: str, group_key_resource_counter: Dict):
    """
    Converts a single source file to FHIR resource(s)

    :param file_path: The file path
    :param config_dir_path: The configuration directory path
    :param output_dir_path: The output directory path
    :param group_key_resource_counter: Keeps a running count of resource counts per group key. Used for generating file
        names.
    :raises FileNotFoundError: if paths are not found

    """
    print(f"File path = {file_path}")
    print(f"Config directory = {config_dir_path}")
    print(f"Output directory = {output_dir_path}")

    filtered_files = _filter_input_files([file_path], config_dir_path)
    print(f"Processing {len(filtered_files)} file(s)")

    if not filtered_files:
        print(f"File {file_path} did not match a DataContract FileDefinition")
    else:
        _convert_source_file(group_key_resource_counter, output_dir_path, file_path, config_dir_path)

    print("Processing complete")


def _convert_directory_files(base_dir_path: str, output_dir_path: str, group_key_resource_counter: Dict):
    """
    Converts all source files within a standard directory layout.

    Input files are parsed from <base dir path>/input.
    Config file are parsed from <base dir path>/config.

    :param base_dir_path: The base directory path used for the conversion process.
    :param output_dir_path: The path to the output directory where FHIR resources are generated.
    :param group_key_resource_counter: Keeps a running count of resource counts per group key. Used for generating file
        names.
    :raises FileNotFoundError: if directory paths are not found
    """
    input_dir_path = f"{base_dir_path}/input"
    config_dir_path = f"{base_dir_path}/config"

    paths = [input_dir_path, config_dir_path, output_dir_path]
    validate_paths(paths, raise_exception=True)

    print(f"Base directory = {base_dir_path}")  # base directory
    print(f"Config directory = {config_dir_path}")
    print(f"Files directory = {input_dir_path}")  # actual source files
    print(f"Output directory = {output_dir_path}")

    input_files: List[str] = []
    for dir_item in os.listdir(input_dir_path):
        if dir_item.startswith("."):
            continue

        item_path = f"{os.path.abspath(input_dir_path)}/{dir_item}"
        input_files.append(item_path)

    filtered_files = _filter_input_files(input_files, config_dir_path)
    print(f"Processing {len(filtered_files)} file(s)")

    for file_path in filtered_files:
        print(f"Processing file = {file_path}")

        _convert_source_file(group_key_resource_counter, output_dir_path, file_path, config_dir_path)

    print("Processing complete")


def convert_to_fhir(args):
    """
    Converts CSV, or delimited records, to FHIR resources.

    The converter may run in either directory or file mode. Directory mode is specified with
    the "-d" flag, while file mode is specified with "-f".

    In directory mode, the "-d" flag is used to specify the base processing directory. Within the
    base processing directory, the converter will parse source files from <directory>/input and configuration
    from <directory>/config.

    In file mode, the "-f" flag is used to specify a single file to convert. File mode also requires the "-c" flag
    to indicate the location of the configuration directory.

    In both modes, the "-o" flag is use to specify the output directory for the converter FHIR resource files.
    FHIR resources are stored within the output directory under "group key subdirectories", which follow the naming
    standard [group key]-[resource type]-[auto-increment-number].json

    :param args: Parsed command line arguments
    :raise: FileNotFoundError if the profile or output directories do not exist
    :raise: ArgumentError if neither -d or -f is received
    """
    # provides a counter for each group key resource
    group_key_resource_counter = {}

    # determine if we're running in directory or file mode
    is_directory_mode = bool(args.d)
    output_dir_path = os.path.expandvars(args.o)

    if is_directory_mode:
        base_dir_path = os.path.expandvars(args.d)
        _convert_directory_files(base_dir_path, output_dir_path, group_key_resource_counter)
    else:
        file_path = os.path.expandvars(args.f)
        config_dir_path = os.path.expandvars(args.c)
        _convert_single_file(file_path, config_dir_path, output_dir_path, group_key_resource_counter)


def _convert_source_file(
        group_key_resource_counter: dict,
        output_dir: str,
        source_file_path: str,
        config_dir_path: str):
    """
    Converts a delimited source file to FHIR resources.

    :param group_key_resource_counter: a dictionary counter used to track group key FHIR resources.
    :param output_dir: directory to place output folders and files
    :param source_file_path: source file path
    :param config_dir_path: the path to the configuration directory
    """
    os.environ["MAPPING_CONFIG_DIRECTORY"] = config_dir_path

    for error, group_key, resources in convert(source_file_path):
        if error:
            print(f"Error processing Group Key = {group_key} in File = {source_file_path}")
            return

        if group_key not in group_key_resource_counter:
            group_key_resource_counter[group_key] = defaultdict(int)

        group_key_dir = f"{output_dir}/{group_key}"
        if not os.path.exists(group_key_dir):
            os.mkdir(group_key_dir)

        try:
            resources_data: List[Dict] = [json.loads(r) for r in resources]
            _write_fhir_resources(resources_data, group_key, group_key_dir, group_key_resource_counter)
        except JSONDecodeError as je:
            print(f"Error decoding FHIR resource Group Key = {group_key} in File = {source_file_path}")
            print(f"{je}")
            return


def _write_fhir_resources(
        resources_data: List[Dict],
        group_key: str,
        group_key_dir: str,
        group_key_resource_counter: dict):
    """
    Writes FHIR resources to disk, within the "group key" directory.

    :param resources_data: list of resources to write
    :param group_key: group_key the fixture file is mapped to in the group_key_resource_counter
    :param group_key_dir: directory of group where the file will be written
    :param group_key_resource_counter: a dictionary map of resources for each group_key
    """
    for r in resources_data:
        resource_type = r.get("resourceType")
        source_file_id = _get_safe_file_id_and_line_number(r.get("meta", []))
        # Use a combination of resource_type with origination file name (source file id) to count up
        combo_resource_type_and_source_file_id = resource_type + "-" + source_file_id
        resource_count = group_key_resource_counter[group_key][combo_resource_type_and_source_file_id] + 1
        group_key_resource_counter[group_key][combo_resource_type_and_source_file_id] = resource_count
        resource_count_display = str(resource_count).zfill(5)

        fixture_file_name = f"{group_key}-{resource_type}-{source_file_id}-{resource_count_display}.json"
        fixture_path = os.path.join(group_key_dir, fixture_file_name)

        with open(fixture_path, "w") as w:
            w.write(json.dumps(r, indent=4, sort_keys=True))


def _get_safe_file_id_and_line_number(extension: List[Dict]) -> str:
    inner_ext = extension.get("extension", [])
    for ext in inner_ext:
        if ext["url"] is not None and "source-file-id" in ext["url"]:
            value_sans_line_number = ext["valueString"].split(":")[0]
            value_sans_line_number = value_sans_line_number.split(".csv")[0]
            return re.sub(r"[^A-Za-z0-9\-]", "_", value_sans_line_number)
    return ""
