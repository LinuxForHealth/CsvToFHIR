from linuxforhealth.csvtofhir.config import ConverterConfig, get_converter_config


def test_converter_config():
    c = ConverterConfig()
    expected_path = f"{c.mapping_config_directory}/{c.mapping_config_file_name}"
    assert expected_path == c.configuration_path


def test_get_converter_config():
    c = get_converter_config()
    expected_path = f"{c.mapping_config_directory}/{c.mapping_config_file_name}"
    assert expected_path == c.configuration_path
