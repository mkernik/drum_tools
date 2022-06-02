# Processing tools for DRUM
This repository contains a collection of python scripts and tools to help with efficiently processing submissions to the Data Repository at the University of Minnesota (DRUM)

## Features 
* Automated Readme tool  (DRUM_automated_readme.py) : Create a readme from the information provided by researchers during the submission process
* Metadata log tool (DRUM_metadata_log.py): Create a metadata log with a list of the content files and metadata for the submission 

## Requirements

* [Python 3](https://www.python.org/) (tools built with version 3.7.11) with additional library [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## How to use
* Download or clone this repository folder to your computer
* Open the Command Prompt (windows) or Terminal (mac).
* Change the working directory to the location of the script

  **Example:** cd path/of/script

* Open Python, call the script, and provide 1) the handle URL of the submission  2) the path of the folder where you would like the readme or metadata log file created

  **Windows example:** py DRUM_automated_readme.py https://hdl.handle.net/11299/185412 path/to/folder

  **Mac example:** python DRUM_automated_readme.py https://hdl.handle.net/11299/185412 path/to/folder


## Author / Contributors

Melinda Kernik - [University of Minnesota Borchert Map Library](https://www.lib.umn.edu/about/staff/melinda-kernik)

Valerie Collins - [University of Minnesota Libraries](https://www.lib.umn.edu/about/staff/valerie-collins)

## License

This project is licensed under Creative Commons Attribution-NonCommercial [(CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/)
