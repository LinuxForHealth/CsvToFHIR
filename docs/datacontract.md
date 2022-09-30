# Data Contract

The CSVToFHIR converter Data Contract file is a JSON based configuration file which defines the CSVToFHIR
conversion process. A single data contract file is used to support multiple CSVToFHIR conversions for a single tenant. 

## Resource Mapping Specification

### Top Level Keys
```json
{
  "general": {},
  "fileDefinitions": {}
}
```

| Key Name        | Description                                                                                                              | Required |
| :-------------- | :----------------------------------------------------------------------------------------------------------------------- | :------- |
| general         | Contains general settings for the CSVToFHIR service which apply to all file definitions such as tenant id, timezone, etc | Y        |
| fileDefinitions | Defines the CSVToFHIR mapping configuration for each CSV source file                                                     | Y        |

### General 
```json
{
  "general": {
    "timeZone": "US/Eastern",
    "tenantId": "tenant1",
    "assigningAuthority": "default-authority",
    "streamType": "live",
    "emptyFieldValues": [
      "empty",
      "\\n"
    ],
    "regexFilenames": true
  }
}
```

| Key Name           | Description                                                                                                   | Required |
| :----------------- | :------------------------------------------------------------------------------------------------------------ | :------- |
| timeZone           | The default timezone to apply to datetime values as necessary. The timeone is a valid tz database/IANA values | Y        |
| tenantId           | The customer tenant id                                                                                        | Y        |
| assigningAuthority | The default assigning authority/system of record, applied to code values where needed                         | N        |
| streamType         | Indicates if the incoming data is "historical" or "live"                                                      | Y        |
| emptyFieldValues   | Additional field values which are treated as "empty" or NULL                                                  | N        |
| regexFilenames     | Determines if the filename to fileDefinition matching will be regex based or simple string comparison. Default: False | N        |



#### Validations
- timeZone is a valid value as specified by `pytz.common_timezones`
- streamType is either historical or live

### FileDefinition
The top-level key within a FileDefinition serves as the FileDefinition name. This name is matched against the input CSV file using either string match (case-insensitive) or regex (case-sensitive) [see general.regexFilenames setting].

Two methods of providing a fileDefinition for a file are supported; inline and external.

#### Inline
Provided as the value of the filename pattern key
```json
{
 "fileDefinitions": {
    "Patient": {
     "comment": "patient demographic fields",
      "fileType": "csv",
      "valueDelimiter": ",",
      "convertColumnsToString": true,
      "resourceType": "Patient",
      "groupByKey": "patientId",
      "skiprows": [2],
      "headers": [],
      "tasks": []
    }
  }
}
```

| Key Name               | Description                                                                                                                                                                                                                              | Required |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- |
| fileType               | The type of source file. Supports "csv" or "fixed-width". Defaults to "csv"                                                                                                                                                              | N        |
| valueDelimiter         | The value, or field, delimiter used in the "CSV" file. Defaults to ","                                                                                                                                                                   | N        |
| comment                | Provides an additional description/comment for the file definition                                                                                                                                                                       | N        |
| convertColumnsToString | When true converts all input columns to Python's "str" data type. If False, Pandas will infer the datatype. Defaults to True.                                                                                                            | N        |
| resourceType           | The target FHIR resource type.                                                                                                                                                                                                           | Y        |
| groupByKey             | The field used to associate the record with other records in separate CSV payloads                                                                                                                                                       | Y        |
| skiprows               | Skip rows from the csv file. Value can be in integet to skip that many lines from the top, or an array to skip rows with that index (0 based). e.g. `[2, 3]` will skip row 3 and 4 from the file (including headers)                     | N        |
| headers                | Provides a header record for a CSV source file without a header. Column names reflect the target record format. When `fileType=fixed-width`, headers is a required field, and should be a dictionary of type <col_name>:<col_width>      | N        |
| tasks                  | List of tasks to execute against the CSV source data, prior to FHIR conversion.                                                                                                                                                          | N        |

#### External
reference an external json file that contains the fileDefinition model. The path can be absolute or relative to the main data-contract
```json
{
 "fileDefinitions": {
    "Patient": "external-patient-file-definition.json"
  }
}
```

#### Validations

- resourceType is a valid FHIR resource type name
- tasks definitions align with pipeline task function implementations
- if fileType is `fixed-width` headers are mandatory


### Tasks

```json
{
 "name": "add_constant",
 "comment": "adds a default ethnic system code to the source data",
 "params": {
    "name": "ethnicitySystem",
    "value": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity"
 }
}
```


| Key Name | Description                                   | Required |
| :------- | :-------------------------------------------- | :------- |
| name     | The task name                                 | Y        |
| comment  | Additional comment/documentation for the task | N        |
| params   | Dictionary of task parameters                 | N        |


#### Supported Tasks

<table>
  <tr>
    <th>Task Name</th>
    <th>Description</th>
    <th>Parameters</th>
    <th>Examples</th>
  </tr>
  <tr>
    <td>add_constant</td>
    <td>Creates an additional column with constant value assigned</td>
    <td>
      <b>name:</b> constant name used as the new column name<br>
      <b>value:</b> constant value
    </td>
    <td>
      <pre>
{
  "name": "add_constant",
  "params": {
    "name": "ssnSystem",
    "value": "http://hl7.org/fhir/sid/us-ssn"
  }
}
      </pre>
    </td>
  </tr>
  <tr>
    <td>add_row_num</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>append_list</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>build_object_array</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>change_case</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>compare_to_date</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>conditional_column</td>
    <td> Creates a new column by mapping the values from a source column to a target value.  Supports inline mappings as a dictionary, and external mappings using a file name.<br><br>If mapping not found:<br>
          <b>"default": value</b> will be used if present<br>
          otherwise leave existing value from source
    </td>
    <td><b>source_column:</b> The source column for the new conditional column
    <b>condition_map:</b> Maps values from the source column to the desired target values or a filename that contains the mappings.
    <b>target_column:</b> The new target column</td>
    <td>
      Inline mapping:
      <pre>
{
  "name": "conditional_column",
  "params": {
    "source_column": "raceText",
    "target_column": "raceCode",
    "condition_map": {
      "american indian": "1002-5",
      "asian": "2028-9",
      "black": "2054-5",
      "pacific islander": "2076-8",
      "white": "2106-3",
      "default": "2131-1"
    }
  }
}
      </pre>
      External file map:
      <pre>
{
  "name": "conditional_column",
  "params": {
    "source_column": "raceText",
    "target_column": "raceCode",
    "condition_map": "race.csv"
  }
}
      </pre>
    </td>
  </tr>
  <tr>
    <td>conditional_column_update</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>condition_column_with_prerequisite</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>convert_to_list</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>copy_columns</td>
    <td>Copies one or more source columns to a target column.</td>
    <td>
      <b>columns:</b> List of column(s) to copy<br>
      <b>target_column:</b> Name of column to be created<br>
      <b>value_separator:</b> Character to be used when mutliple columns are concatenated.Defaults to a " ".
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>filter_to_columns</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>find_not_null_value</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>format_date</td>
    <td>Formats date string values within a column to a target format.</td>
    <td>
      <b>columns:</b>  the column name(s) to update<br>
      <b>date_format:</b> the date format to apply to the column(s). Defaults to “%Y-%m-%d”</td>
    <td>
      <pre>
{
  "name": "format_date",
  "params": {
    "columns": [
      "dateOfBirth"
    ],
    "date_format": "%Y-%m-%d"
  }
}
      </pre>
    </td>
  </tr>
  <tr>
    <td>map_codes</td>
    <td>Maps 'codes' values to a target representation.  map_codes supports inline mappings as a dictionary, and external mappings using a file name.  If a map of “default” is provided, any value that does not match another mapping key is given this value. 
    </td>
    <td>
      <b>code_map:</b> Contains a mapping from source value to target value for a given set of fields or the name of a file which contains the mappings.
    </td>
    <td>
      Internal data contract mapping
      <pre>
{
  "name": "map_codes",
  "params": {
    "code_map": {
      "sex": {
        "default": "unknown",
        "F": "female",
        "M": "male",
        "O": "other"
      }
    }
  }
}
      </pre>
      External mapping:
      <pre>
{
  "name": "map_codes",
  "params": {
    "code_map": {
      "sex": "sex.csv"
    }
  }
}
      </pre>
    </td>
  </tr>
  <tr>
    <td>rename_columns</td>
    <td>Renames column(s)</td>
    <td><b>column_map:</b> A dictionary which maps the source column names to the target column names.</td>
    <td>
      <pre>
{
  "name": "rename_columns",
  "params": {
    "column_map": {
      "hospitalId": "assigningAuthority",
      "givenName": "nameFirstMiddle",
      "familyName": "nameLast",
      "sex": "gender",
      "dateOfBirth": "birthDate"
    }
  }
}
      </pre>
    </td>
  </tr>
  <tr>
    <td>replace_text</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>remove_whitespace_from_columns</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>set_nan_to_none</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>split_column</td>
    <td></td>
    <td></td>
    <td>
      <pre>
      </pre>
    </td>
  </tr>
  <tr>
    <td>split_row</td>
    <td>
    Splits a record “row” on a column or columns, creating N additional rows for each column included within the split operation. Creates additional columns for the “label” and “value”.</td>
    <td>
      <b>columns:</b> The column(s) to split on<br>
      <b>split_column_name:</b> The column name or header used for the "label" column<br>
      <b>split_value_column_name:</b> The column name or header used for the "value" column
    </td>
    <td>
      <pre>
{
  "name": "split_row",
  "params": {
    "columns": [
      "height",
      "weight",
      "bmi"
    ],
    "split_column_name": "observationCodeText",
    "split_value_column_name": "observationValue"
  }
}
      </pre>
    </td>
  </tr>
</table>


## Alternative Datacontract locations
CsvToFHIR uses the [smart_open](https://github.com/RaRe-Technologies/smart_open) library to read the Datacontract and any referenced file definitions within it.
This allows CsvToFHIR to seamlessly support data contract files that are stored in external cloud storage such as S3, Azure Blob Storage etc. (see smart_open documentation for
a full list of supported platforms).

In order to use an external cloud storage vendor additional dependencies might be required which are not automatically installed by CsvToFHIR. For example to support
azure storage, install the `azure` extras package from the smart_open `pip install smart_open[azure]`. Again, see the smart_open documentation for additional information
and examples.

A sample configuration to use a data contract stored in azure would look like:
```
export mapping_config_directory=azure://my_bucket/my_prefix/
export mapping_config_file_name=data-contract.json
```