# CSV to FHIR

Loads CSV records from file, and maps them to FHIR resources.

## Pre-requisites

- [Python](https://www.python.org/downloads/) >= 3.9 for application development

## Quickstart CLI

```shell
# clone the repo
git clone https://github.com/LinuxForHealth/csv2hir
cd csvtofhir

# create virtual environment and create an "editable" install
python3 -m venv venv && source venv/bin/activate && python3 -m pip install --upgrade pip setuptools
python3 -m pip install -e .[dev]
# run tests
python3 -m pytest
```

The CSVToFHIR CLI supports:

### DataContract validation
```shell
csvtofhir% csvtofhir validate -f tests/resources/data-contract/data-contract.json
```

### CSV Conversion

The csvtofhir convert command has two processing modes, directory mode, `-d`, and file mode, `-f`.

#### Directory Mode
In `directory` mode the convert command is given a base directory path which contains the following subdirectories:
- input: where input, or source, data records are located
- config: where the CSVToFHIR data contract configuration, data-contract.json, and supporting files are located.

The `-o` parameter is used to specify the location where output files are saved.

```shell
csvtofhir convert -d /data/csv-data  -o /data/output
```

#### File Mode
In `file` mode the convert command is provided a single file path to convert.
The `-f` flag is used to specify the input data file.
The `-c` flag is used to specify the configuration directory.
The `-o` flag is used in the same manner as `directory` mode.

```shell
csvtofhir convert -f /data/csv-data/Patient.csv -c /data/config  -o /data/output
```

## Code Formatting

CSVToFHIR uses [flake8](https://flake8.pycqa.org/en/latest/) for style checking and [autopep8](https://pypi.org/project/autopep8/) for formatting.
Flake8 is used to find and identify issues, while AutoPep8 will fix (most of) them.

A simplified workflow to ensure uniform formatting is to . . .

Run AutoPep8 against the source and test code

```shell
python3 -m autopep8 src/ tests/ --in-place
```

And then use Flake8 to find remaining issues, which will need to be manually addressed.
```shell
python3 -m flake8 src/ tests/
```

Flake8 and AutoPep8 are configured using [setup.cfg](./setup.cfg) within the `flake8` section.

In VS Code to format in the editor, `- in-place` must be removed from the configuration.

## Logging

CSVToFHIR follows [best practices](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library) for logging configuration. Specifically,
the only handler supported is the [NullHandler](https://docs.python.org/3/library/logging.handlers.html#logging.NullHandler). This allows consuming applications and services to configure handlers as appropriate.

The following table lists packages which emit logging information.

| Packages     | Description                                                        |
|:------------------|:-------------------------------------------------------------------|
| csvtofhir          | CSVToFHIR converter entry point                                    |
| csvtofhir.fhirrs   | Converts CSV source records to FHIR Resources                      |
| csvtofhir.pipeline | Pipeline tasks used to align source data with internal CSV models  |

To utilize logging within a local development environment, please review the comments within the [support module](src/linuxforhealth/csvtofhir/support.py).

## Additional Documentation
- [DataContract Design](docs/datacontract.md)
- [Implementation Guide](docs/implementation-guide.md)
- [Internal Format Guide](docs/internal-format.md)
- [IDE Configuration](docs/ide.md)
