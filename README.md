# Voicebrief

Converts video / audio conversations to text and subsequently provides a summary into a managable report.

## Installation

Clone the repository. Use the dependency and package manager [Poetry](https://python-poetry.org/) to install all the dependencies of Nelumbo.

```bash
poetry install
```

## Configuration for usage with OpenAI

Create a text file _"dev.env"_ in the root of the project. This will contain the "OPENAI_API_KEY" environment variable used by the application to obtain the token associated to a valid OpenAI account when calling the API.

```bash
OPENAI_API_KEY=sk-A_seCR_et_key_GENERATED_foryou_by_OPENAI
```
The environment variables are loaded into the execution context of the application when run in the debugger if as such specified in the file _"launch.json"_. An example launch configuration shows how:

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Module",
            "type": "python",
            "request": "launch",
            "module": "nelumbo",
            "justMyCode": true,
            "args":["-d","pascal"],
            "envFile": "${workspaceFolder}/dev.env"
        }
    ]
}
```
## Usage

TODO

## Development
[Activate the Python virtual environment](https://python-poetry.org/docs/basic-usage/#activating-the-virtual-environment) with

```bash
poetry shell
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Copyright and license

Copyright © 2024 Iwan van der Kleijn

Licensed under the MIT License 
[MIT](https://choosealicense.com/licenses/mit/)