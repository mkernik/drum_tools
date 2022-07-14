# Processing tools for DRUM
This repository contains a collection of python scripts and tools to help with efficiently processing submissions to the Data Repository at the University of Minnesota (DRUM)

## Features
* DRUM_Curator_Tools.ipynb: A CoLab Notebook with scripts to create a metadata log, Readme.txt, and Datacite XML for DRUM submissions.  
* Download files tool (DRUM_downloadFiles.py): Creates a folder and downloads the content files from a DRUM submission.  An [executable version of this tool](https://z.umn.edu/DRUM_downloadFiles) is available for Windows only.   
* tools_development: This folder contains alternative versions of scripts and tools that are under development. Note: these scripts are not being kept fully in sync with the CoLab Notebook.

## Requirements

* [Python 3](https://www.python.org/) (tools built with version 3.7.11) with additional library [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## How to use

### Colab Notebook
* Click on DRUM_Curator_Tools.ipynb in the list of files above
* Click on the "Open in Colab" button at the top of the page

### Other scripts in the repository
* Download or clone this repository folder to your computer
* Open the Command Prompt (windows) or Terminal (mac)
* Change the working directory to the location of the script

  **Example:** cd path/of/script

* Open Python and call the script. 

  **Windows example:** py DRUM_downloadFiles.py

  **Mac example:** python DRUM_downloadFiles.py

An interface will open allowing you to enter the handle URL for a DRUM submission (e.g. https://hdl.handle.net/11299/228067).  Click "Download Files" and view progress in the black console window that opens along with the interface.  

## Author / Contributors

Melinda Kernik - [University of Minnesota Borchert Map Library](https://www.lib.umn.edu/about/staff/melinda-kernik)

Valerie Collins - [University of Minnesota Libraries](https://www.lib.umn.edu/about/staff/valerie-collins)

## License

This project is licensed under Creative Commons Attribution-NonCommercial [(CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/)
