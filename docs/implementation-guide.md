# CSVToFHIR Implementation Guide

This guide provides an overview of the steps required to support a new mapping within the CSVToFHIR converter.

## Source Data Review

The following steps are helpful when reviewing source data:

- Confirm that it is a "content complete" record, meaning that the data record includes all required fields from a FHIR specification and use-case perspective.
- Verify that delimiters are used consistently
- Verify that field values are consistent (date fields are dates, code fields have uniform values, etc)

## Create Data Contract

The CSVToFHIR project contains several "test" data contracts which may be used as initial templates.
[data-contract.json](../tests/resources/data-contract/data-contract.json) uses a `rename_columns` configuration which is helpful for source files with a header row.
For files without a header row, refer to [data-contract-headers.json](../tests/resources/data-contract/data-contract-headers.json).

### The General Section

For new implementations, implement the `general` document. When reviewing the `general` document consider:

- timeZone: Which time zone should be used as the "default" time zone?
- tenantId: What is the customer's tenant id?
- assigningAuthority: The assigning authority serves as the "default" system for FHIR codeable concepts and values.
- streamType: Is the data stream used for live or historical data?
- emptyFieldValues: Does the CSV file use codes or terms to indicate empty field value? Please refer to the [Pandas csv_reader documentation](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
for a list of values currently treated as empty/null.

### File Definition Section

The key associated with the FileDefinition settings must be a valid case-insensitive substring of the source CSV data file.
For instance the key "Patient" supports any of the following files:

- 2022-02-18-patient.csv
- 2022-02-18-patient.dat
- Patient20220218.csv

### File Definition Fields

When reviewing the FileDefinition, consider the following:

- valueDelimiter: How are fields, or values, within the file delimited? Defaults to "," (comma)
- resourceType: What is the target FHIR resource type?
- groupByKey: What key within the source record should be used to link records across CSV source files?
- headers: If the source does not contain a header row, use the `headers` key to specify a header row.
- tasks: Tasks are used to pre-process and update data fields prior to converting to a FHIR resource.

### Data Contract Comments

Additional information, or comments, may be applied to FileDefinition, Task, and Header definitions within the DataContract.
Comments serve as additional documentation for the DataContract and should be used to clarify the significance of the element 
within the overall DataContract.

### Validate Data Contract
Once the Data Contract is complete, validate the configuring using the csv2fhir utility:

```shell
csvtofhir%  csvtofhir -v tests/resources/data-contract.json
```

### Tasks
Tasks are used to update source CSV records to the target internal format, prior to conversion. Within the Data Contract,
tasks are expressed as an ordered list of items where order is preserve for task execution and results are chained to form
a "pipeline".

In the example below, the `add_constant` tasks executes the [add_constant function](../src/linuxforhealth/csvtofhir/pipeline/tasks.py) with
the parameters/arguments `name` and `value`:
```json
      "tasks": [
        {
          "name": "add_constant",
          "params": {
            "name": "ethnicitySystem",
            "value": "http://terminology.hl7.org/CodeSystem/v2-0189"
          }
        },
      { etc }
]
```

#### Task Functions
Task specifications are resolved to functions defined within the [pipeline task module](../src/linuxforhealth/csvtofhir/pipeline/tasks.py).
The pipeline framework provides the `data_frame` argument and uses the task's `param` values to convey additional arguments.

```python
from pandas import DataFrame
from typing import Any

def add_constant(data_frame: DataFrame, name: str, value: Any) -> DataFrame:

    if name in data_frame.columns.to_list():
        raise TaskException(f"Unable to add constant {name}")
    data_frame[name] = value
    return data_frame
```

## Converter Implementations
Each target FHIR resource has a converter module located in the [fhirrs package](../src/linuxforhealth/csvtofhir/fhirrs). Each converter module
implements a `convert_record` function which takes an input record from the CSV and according to the data contract return a FHIR resource.  `convert_record` has the following signature:

```python
def convert_record(group_by_key: str, record: Dict, resource_meta: Meta = None) -> List[str]:
    pass
```

The `convert_record` function accepts the following arguments:

- group_by_key: associates records across CSV files
- record: the source CSV record
- Meta: a FHIR Meta Resource model appended to the converted record (Optional)

The resource specific `convert_record` implementations are integrated in the [fhirrs converter](../src/linuxforhealth/csvtofhir/fhirrs/converter.py)
