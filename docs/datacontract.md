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

| Key Name        | Description                                                                                                             | Required |
|:----------------|:------------------------------------------------------------------------------------------------------------------------|:---------|
| general         | Contains general settings for the CSVToFHIR service which apply to all file definitions such as tenant id, timezone, etc | Y        |
| fileDefinitions | Defines the CSVToFHIR mapping configuration for each CSV source file                                                  | Y        |

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
    ]
  }
}
```

| Key Name           | Description                                                                                                   | Required |
|:-------------------|:--------------------------------------------------------------------------------------------------------------|:---------|
| timeZone           | The default timezone to apply to datetime values as necessary. The timeone is a valid tz database/IANA values | Y        |
| tenantId           | The customer tenant id                                                                                        | Y        |
| assigningAuthority | The default assigning authority/system of record, applied to code values where needed                         | N        |
| streamType         | Indicates if the incoming data is "historical" or "live"                                                      | Y        |
| emptyFieldValues   | Additional field values which are treated as "empty" or NULL                                                  | N        |


#### Validations
- timeZone is a valid value as specified by `pytz.common_timezones`
- streamType is either historical or live

### FileDefinition
The top-level key within a FileDefinition serves as the FileDefinition name. This name is matched against the input CSV file (case-insensitive)
```json
{
 "fileDefinitions": {
    "Patient": {
     "comment": "patient demographic fields",
      "valueDelimiter": ",",
      "convertColumnsToString": true,
      "resourceType": "Patient",
      "groupByKey": "patientId",
      "headers": [],
      "tasks": []
    }
  }
}
```

| Key Name               | Description                                                                                                                   | Required |
|:-----------------------|:------------------------------------------------------------------------------------------------------------------------------|:---------|
| valueDelimiter         | The value, or field, delimiter used in the "CSV" file. Defaults to ","                                                        | N        |
| comment                | Provides an additional description/comment for the file definition                                                            | N        |
| convertColumnsToString | When true converts all input columns to Python's "str" data type. If False, Pandas will infer the datatype. Defaults to True. | N        | 
| resourceType           | The target FHIR resource type.                                                                                                | Y        |
| groupByKey             | The field used to associate the record with other records in separate CSV payloads                                            | Y        |
| headers                | Provides a header record for a CSV source file without a header. Column names reflect the target record format                | N        |
| tasks                  | List of tasks to execute against the CSV source data, prior to FHIR conversion.                                               | N        |

#### Validations

- resourceType is a valid FHIR resource type name
- tasks definitions align with pipeline task function implementations


### Tasks

```json
{
 "name": "add_constant",
 "comment": "adds a default ethnic system code to the source data",
 "params": {
    "name": "ethnicitySystem",
    "value": "http://terminology.hl7.org/CodeSystem/v2-0189"
 }
}
```


| Key Name | Description                                   | Required |
|:---------|:----------------------------------------------|:---------|
| name     | The task name                                 | Y        |
| comment  | Additional comment/documentation for the task | N        |
| params   | Dictionary of task parameters                 | N        |


#### Supported Tasks

<table>
<tr>
    <th>Task Name</th>
    <th>Description</th>
    <th>Parameters</th>
    <th>Examples</th></tr>
<tr>
    <td>add_constant</td>
    <td>Creates an additional column with constant value assigned</td>
    <td>name<br>value</td>
    <td>
    
    ```json
    json
    {
    "name": "add_constant",
    "params": {
    "name": "ssnSystem",
    "value": "http://hl7.org/fhir/sid/us-ssn"
    }
    }
    ```
    
    </td>
</tr>
</table>


