<!--
# Steven G. Opferman | steven.g.opferman@gmail.com
# My personal template for README.md files, because I'm lazy :P
# Adapted from:
#   https://github.com/othneildrew/Best-README-Template/
#   https://github.com/kylelobo/The-Documentation-Compendium/
-->

<!--
<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/6wj0hh6.jpg" alt="Project logo"></a>
</p>
-->

<h1 align="center">Resume Parser</h1>
<div id="top"></div>

<!--
The cute little icon things.

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/kylelobo/The-Documentation-Compendium.svg)](https://github.com/kylelobo/The-Documentation-Compendium/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kylelobo/The-Documentation-Compendium.svg)](https://github.com/kylelobo/The-Documentation-Compendium/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>
-->

<p align="center">
A Python script to scan resumes for signals of elite class status.
<br>
</p>

## Table of Contents

- [About](#about)
- [Usage](#usage)
- [Getting Started](#getting_started)
- [Contributing](#contributing)
<!-- - [Acknowledgements](#acknowledgements) -->

## About <a name="about"></a>

Anonymous screening seems to be a good solution for reducing bias in hiring. However, it may not be possible to fully anonymize a resume, particularly in regards to class status (elite vs. non-elite), because class is signalled in many subtle ways. This script searches resumes for terms that signal elite class status and counts them, outputting a CSV intended to be loaded into Stata for analysis.

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage <a name="usage"></a>

```sh
python take5.py
```

<!-- _For more examples, please refer to the [Documentation](https://example.com)_ -->

<p align="right">(<a href="#top">back to top</a>)</p>

## Getting Started <a name="getting_started"></a>

These instructions will get you a copy of the project up and running.

### Prerequisites

The things you need to use the software and how to install them.

### Installation

1. Clone the repo:

    ```sh
    git clone https://github.com/TheFirstQuestion/resume-parser.git
    ```

2. Install dependencies:

    ```sh
    mamba install textract nltk tqdm pandas
    ```

3. Run `setup.py` (once, ever) to download and generate necessary files:

    ```sh
    python setup.py
    ```

4. Edit the config section at the top of the script to suit your needs.

    | Variable  | Usage | Suggested Value |
    | --------  | ------------------- | --------------------- |
    | `RESUME_DIRECTORY` | Path (relative to script location) to the directory containing the resumes.   | `"./sample_resumes/"` |
    | `TERMS_LOCATION` | Path (relative to script location) to the directory containing the CSV file(s) defining the terms of interest. | `"./terms_of_interest/"` |
    | `OUTPUT_DIRECTORY` | Path (relative to script location) to the directory wherein the script will write the output files.  | `"./output/"` |
    | `RESUME_ID_COLUMN_NAME` | The header for the CSV column that identifies each resume. | `"resumeName"` |
    | `SKIP_GREEK` | Should the script skip searching for all the Greek terms of interest? | `True` |

5. Run the script.

    ```sh
    python take5.py
    ```

<p align="right">(<a href="#top">back to top</a>)</p>

## Contributing <a name="contributing"></a>

Collaboration is what makes the world such an amazing place to learn, inspire, and create. **Any contributions or suggestions you make are greatly appreciated!**

Feel free to do any of the following:

- send me an [email](mailto:sopferman@stanford.edu)
- open an issue
- fork the repo and create a pull request

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ## Acknowledgements <a name="acknowledgements"></a>

- Hat tip to anyone whose code was used
- Inspiration
- References

<p align="right">(<a href="#top">back to top</a>)</p> -->
