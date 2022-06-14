# Graphical User Interface Tools
This folder contains experiments in ways to distribute scripts as GUI tools to curators at the Data Repository at the University of Minnesota (DRUM)

## Features
There are two version of the tool, both with options to:
* download files associated with a submission
* create a metadata log
* create a readme
* create an XML that can be used to create a DOI through Datacite

DRUM_combined_tkinter.py contains all of the code in a single script.

tkinter_interface.py contains just the user interface and draws on modules (download_files.py, metadata_log.py, automated_readme.py, datacite_xml.py) to perform the curation actions

## Requirements

* [Python 3](https://www.python.org/) (tools built with version 3.7.11) with additional library [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## How to use

* Download or clone this repository folder to your computer
* Open the Command Prompt (windows) or Terminal (mac).
* Change the working directory to the location of the script

  **Example:** cd path/of/script

* Open Python and call the script .

  **Windows example:** py DRUM_metadata_log_tkinter.py

  **Mac example:** python DRUM_metadata_log_tkinter.py

* In the dialog box that opens provide 1) the handle URL of the submission  2) the path of the folder where you would like the metadata log file created

## License

This project is licensed under Creative Commons Attribution-NonCommercial [(CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/)
