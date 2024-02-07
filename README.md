# Voicebrief

Converts video / audio conversations to text and subsequently provides a summary into a manageable report.


![Voicebrief converts video / audio conversations to text ](images/voicebrief_small.png)


## Installation

Clone the repository. Use the dependency and package manager [Poetry](https://python-poetry.org/) to install all the dependencies of Voicebrief.

```bash
poetry install
```

## Configuration for usage with OpenAI

Create a text file _"openai_api_key.env"_ in the root of the project. This will contain the "OPENAI_API_KEY" environment variable used by the application to obtain the token associated to a valid OpenAI account when calling the API.

```bash
OPENAI_API_KEY=sk-A_seCR_et_key_GENERATED_foryou_by_OPENAI
```
The key is loaded into the execution context of the application when run from the command line or run in the debugger.

Alternatively, if the file is not present, then 'voicebrief' will look for the environment variable "OPENAI_API_KEY".


## Tests, checks etc

Voicebrief uses the following tools to test and verify the code: 

- [pytest](pytest.org/): my favourite Pythjon testing tool
- [mypy](https://mypy-lang.org/): Optional statical type checking for Python
- [flake8](https://flake8.pycqa.org/): light weight linting tool/style enforcer (PEP8)
- [black](https://github.com/psf/black): Python code formatter

You can run each tool with:

```bash
❯ poetry run tool-name [path]
```

for example:

```bash
❯ poetry run mypy voicebrief
```

or run all tools automatically with:

```bash
❯ poetry run check-all
```
In this case, the 'check-all' command stops running the commands if one fails.

Note that the 'flake8' tool obtains its settings from the '.flake8' config file, not pyproject.toml.

The 'check-all' command is implemented in the dev_env/runchecks.py script. It is run through the associated config section in pyproject.toml.

```bash
[tool.poetry.scripts]
check-all = "devenv.run_checks:run_checks"
```

## Usage

Usage of the tool:

```bash
❯ voicebrief -h
usage: voicebrief [-h] [-v] path [destination]

Voicebrief - Converts video / audio conversations to text and subsequently provides a summary into a managable report.

positional arguments:
  path         Path to the audio file
  destination  Optional destination directory (default: directory of "path" parameter)

options:
  -h, --help   show this help message and exit
  -v, --video  Consider "path" to be a video and extract the audio

```

When dealing with audio files larger than 20Mb, the audio file will be "split" into different files, stored in the sub-directoty "chunks" of the _destination_ path. For each audio file a transcript text will be saved (stored with the prefix "transcript"). All transcripts will be concatedanted and optimized (summarized) in one single file, saved with the prefix "optimized". 

## Development
[Activate the Python virtual environment](https://python-poetry.org/docs/basic-usage/#activating-the-virtual-environment) with

```bash
poetry shell
```

## LEFT TO(BE)DO(NE)

### Prompt engineering (COULD HAVE)

The summary should have certain guarantees related with the key-points and perhaps some meta-data: key participants, tone of conversation etc. 

## FFmpeg Dependency

### Why FFmpeg?

'Voicebrief' utilizes the `moviepy` library for extensive video editing operations. `moviepy` itself relies on `FFmpeg`, a powerful multimedia framework capable of handling a vast array of video and audio formats. This dependency is crucial as `FFmpeg` performs the encoding and decoding of media, allowing 'voicebrief' to manipulate video and audio data effectively.

### Verifying FFmpeg Installation

Before using 'voicebrief', ensure that `FFmpeg` is installed and accessible from your system's command line interface (CLI). Here's how you can verify the installation of `FFmpeg` on different operating systems:

#### Windows

1. Open the Command Prompt.
2. Type `ffmpeg -version` and press Enter.
3. If `FFmpeg` is installed, you will see the version information.
4. If you get an error saying 'ffmpeg' is not recognized, it is not installed.

#### Linux

1. Open a Terminal window.
2. Type `ffmpeg -version` and press Enter.
3. If `FFmpeg` is installed, you will see the version information.
4. If it's not installed, you might see a command suggestion for installation or an error message.

#### macOS

1. Open the Terminal app.
2. Type `ffmpeg -version` and press Enter.
3. If `FFmpeg` is installed, the version information will be displayed.
4. If it's not installed, you'll receive an error message indicating it's not found.

### Installing FFmpeg

If `FFmpeg` is not installed, follow the instructions below for your operating system:

#### Windows

1. Download the `FFmpeg` build from https://ffmpeg.org/download.html#build-windows.
2. Extract the downloaded ZIP file.
3. Add the `bin` folder within the extracted folder to your system's Environment Variables in the Path section.
4. Verify the installation by following the verification steps above.

#### Linux (Ubuntu/Debian)

1. Update your package list: `sudo apt-get update`.
2. Install `FFmpeg` by running: `sudo apt-get install ffmpeg`.
3. Verify the installation using the steps provided in the verification section.

#### macOS

1. Install Homebrew, if it's not already installed, with: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
2. Install `FFmpeg` using Homebrew: `brew install ffmpeg`.
3. Verify the installation using the steps provided in the verification section.

Ensure that `FFmpeg` is correctly installed and configured before proceeding with the usage of 'voicebrief'.


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Copyright and license

Copyright © 2024 Iwan van der Kleijn

Licensed under the MIT License 
[MIT](https://choosealicense.com/licenses/mit/)