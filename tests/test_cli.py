from unittest.mock import MagicMock

import pytest

from linuxforhealth.csvtofhir.cli.main import main


def test_cli_no_args(capfd):
    """
    Confirms that the Help text is printed if no arguments are provided

    :param capfd: pytest fixture used to capture stdout and stderr
    """
    main([])
    out, _ = capfd.readouterr()

    assert "CSVToFHIR converts custom delimited records to FHIR Resources" in out


def test_validate_file_not_found():
    """Validates that a FileNotFound exception is raised for an invalid file path"""
    validate_args = ["validate", "-f", "/tmp/not-a-real-dir/data-contract.json"]

    with pytest.raises(FileNotFoundError):
        main(validate_args)


def test_validate_contract_invalid(data_contract_directory: str, capfd):
    """
    Validates that an invalid data contract writes an error to stdout

    :param data_contract_directory: The data contract directory fixture
    """
    # invalid-data-contract.json is missing the General section, which is required
    contract_path = f"{data_contract_directory}/invalid-data-contract.json"
    validate_args = ["validate", "-f", contract_path]
    main(validate_args)
    out, _ = capfd.readouterr()
    assert "Resource Mapping is invalid" in out


def test_validate(data_contract_directory: str, capfd):
    """
    Tests CLI validate command when arguments are valid

    :param data_contract_directory: The data contract directory fixture
    :param capfd: pytest fixture used to capture stdout and stderr
    """
    contract_path = f"{data_contract_directory}/data-contract.json"
    validate_args = ["validate", "-f", contract_path]
    main(validate_args)

    out, _ = capfd.readouterr()
    assert "DataContract is valid" in out


def test_convert_invalid_file_mode(csv_directory: str, capfd):
    """Validates convert file mode argument validation"""
    file_path = f"{csv_directory}/Patient.csv"
    # -c is required but missing
    convert_args = ["convert", "-f", file_path]

    with pytest.raises(SystemExit):
        main(convert_args)

    _, err = capfd.readouterr()
    assert "-c is required when -f is used" in err


def test_convert_directory_mode(monkeypatch):
    """
    Tests that convert directory mode branching works as expected

    :param monkeypatch: The pytest monkeypatch fixture
    """
    mock_convert = MagicMock()
    monkeypatch.setattr("linuxforhealth.csvtofhir.cli.convert._convert_directory_files", mock_convert)

    convert_args = ["convert", "-d", "/data", "-o", "/output"]
    main(convert_args)
    mock_convert.assert_called()


def test_convert_file_mode(monkeypatch):
    """
    Tests that convert file mode branching works as expected

    :param monkeypatch: The pytest monkeypatch fixture
    """
    mock_convert = MagicMock()
    monkeypatch.setattr("linuxforhealth.csvtofhir.cli.convert._convert_single_file", mock_convert)

    convert_args = ["convert", "-f", "/data/Patient.csv", "-c", "/data/config", "-o", "/output"]
    main(convert_args)
    mock_convert.assert_called()
