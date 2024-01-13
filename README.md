# Voicebrief

Converts video / audio conversations to text and subsequently provides a summary into a manageable report.


![Voicebrief converts video / audio conversations to text ](images/voicebrief_small.png)


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

Usage of the tool:

```bash
Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a managable report.

positional arguments:
  path         Path to the audio file
  destination  Optional destination directory (default: directory of audio file)

options:
  -h, --help   show this help message and exit
```

## Development
[Activate the Python virtual environment](https://python-poetry.org/docs/basic-usage/#activating-the-virtual-environment) with

```bash
poetry shell
```

## LEFT TO(BE)DO(NE)

### MUST HAVE
- Split any audiofile is chunks which the OPENAI API can handle (it would seem the max. size for Speech to text is currently 25 Mb)
- Adjust the app to properly handle this chunkink and change the handling of the transcript and summary text files

### SHOULD HAVE
- Extract sound file from MP4 video file
- Option to remove summary

### Prompt engineering (COULD HAVE)

The summary should have certain guarantees related with the key-points and perhaps some meta-data: key participants, tone of conversation etc. 

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Copyright and license

Copyright © 2024 Iwan van der Kleijn

Licensed under the MIT License 
[MIT](https://choosealicense.com/licenses/mit/)