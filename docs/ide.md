# IDE Configuration

The following sections provide general guidance on running CSVToFHIR convert CLI within an IDE. These configurations
are generally useful for debugging. The instructions below assume that the "Quickstart" setup is complete and a 
virtual environment exists in `csvtofhir/venv`

## Jetbrains Products (IntelliJ, PyCharm)

### Configure Project Interpreter/Virtual Environment

For IntelliJ or IntelliJ Ultimate:
- Select File, Project Structure
- Use the SDK field to browse to the Python interpreter within csvtofhir/venv/python

Note IntelliJ/IntelliJ Ultimate supports Python using a plugin. The IDE will retain it's Java UI components, but these
do not need to be configured.

For PyCharm:
- Select Preferences, search for python interpreter
- Use the Python Interpreter field to browse to csvtofhir/venv/python

### Python Run Configuration

Configure the IDE to run the CSV2FHIR convert CLI with the appropriate parameters.

The following screenshot shows the configuration on a typical developer machine. The IntelliJ and PyCharm
configuration panes will be similar.

![Python Run Configuration](jetbrains-python-config.png)

Enter the command line arguments within the Parameters field

![CLI Parameters](jetbrains-python-config-params.png)

## Visual Studio Code

### Configure Project Interpreter/Virtual Environment

- Select View, Command Palette 
- Type Python Select Interpreter
- Browse to the interpreter under csvtofhir/venv/python

### Python Run Configuration

- Click the Run and Debug icon on the left sidebar
- Select the option to create a "launch.json" file if it does not exist
- If "launch.json" exists, click the settings icon
- Add the "args" key to "launch.json" to support the CLI command and associated parameters
- Save and close the launch.json file (within .vscode directory in project)
- Open src/csvtofhir/cli/main.py
- Click the Run/Debug button

The following launch.json configuration runs the convert CLI in "directory" mode. Note that file paths within the launch
configuration's "args" list are specific to the local development environment.

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true,
            "args": [
                "convert",
                "-d",
                "./data/csv",
                "-o",
                "/data/output"
            ]
        }
    ]
}
```
