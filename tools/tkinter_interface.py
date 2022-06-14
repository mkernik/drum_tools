# -*- coding: utf-8 -*-
"""
script name:DRUM_combined_tkinter.py

inputs: -DRUM handle URL (i.e. https://hdl.handle.net/11299/226188 or https://conservancy.umn.edu/handle/11299/226188)
        -Directory path for the metadata log
outputs: -text file metadata log ("metadata_log_[last 6 numbers of the handle]_")
         -text file readme ("readme_[last 6 numbers of the handle]_")
         -xml file for creating datacite DOIs("doi_metadata_[last 6 numbers of the handle]_")

description: This tkinter script tool can generate three files based on information 
entered by researchers during the submission process to the Data Repository for 
the University of Minnesota (DRUM) and the original files uploaded. 1) A metadata log
used by the curator to keep track of changes made to the submission 2) The start
of a readme file describing the contents of the submission.  This can be sent 
back to the researcher to complete if other documentation has not been provided.
3) An xml that can be uploaded to Datacite to create a DOI for the submission.

last modified: May 2022
authors: Melinda Kernik and Valerie Collins
"""

##import necessary modules and return a message if any are not available
try:
    import tkinter.filedialog
    import tkinter.messagebox
    from tkinter import LabelFrame
    from tkinter import ttk
    import download_files
    import metadata_log
    import automated_readme
    import datacite_xml
    
except Exception as e:
    print(e)

#Create message box if there is an error
def show_error(text):
    tkinter.messagebox.showerror('Error', text)

#Create message box describing results of clicking a button
def show_results(text):
    tkinter.messagebox.showinfo("Results", text)

    
# Create the GUI interface
app = tkinter.Tk()
app.geometry('600x300')
app.title("DRUM Tools")


# Open the folder picker and send selected information to the metadata_log() function.
def click_download_files():
    handle_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    if handle_url and outputDir:
        try:
            download_files.download_files(handle_url, outputDir)
            show_results("Finished downloading files for: " + handle_url)
        except:
            show_error("Unable to download files!")
    elif outputDir:
        show_error("Please enter the URL for a DRUM submission")
    elif handle_url:
        show_error("Please select an output folder")


def click_metadata_log():
    handle_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    if handle_url and outputDir:
        try:
            metadata_log.metadata_log(handle_url, outputDir)
            show_results("Finished creating metadata file for: " + handle_url)
        except:
            show_error("Unable to generate metadata log!")
    elif outputDir:
        show_error("Please enter the URL for a DRUM submission")
    elif handle_url:
        show_error("Please select an output folder")

# Open the folder picker and send selected information to automated_readme() function
def click_readme():
    handle_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    if handle_url and outputDir:
        try:
            automated_readme.automated_readme(handle_url, outputDir)
            show_results("Finished creating readme for: " + handle_url)
        except:
            show_error("Unable to generate README!")
    elif outputDir:
        show_error("Please enter the URL for a DRUM submission")
    elif handle_url:
        show_error("Please select an output folder")

# Open the folder picker and send selected information to datacite_xml() function
def click_doi():
    handle_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    if handle_url and outputDir:
        try:
            datacite_xml.datacite_xml(handle_url, outputDir)
            show_results("Finished creating DataCite DOI metadata for: " + handle_url)
        except:
            show_error("Unable to generate DOI XML!")
    elif outputDir:
        show_error("Please enter the URL for a DRUM submission")
    elif handle_url:
        show_error("Please select an output folder")
        
# Create the window header
header = tkinter.Label(app, text="DRUM Tools!", fg="blue", font=("Cabin", 24))
header.pack(side="top", ipady=20)

# Add the descriptive text
text = tkinter.Label(app, text="""
Enter the handle for a DRUM submission
Example: https://conservancy.umn.edu/handle/11299/226188\n""")
text.pack()

# Draw box for entering the handle URL
entry = ttk.Entry(app, width = 70)
entry.pack(ipady=2)

frame = LabelFrame(app, borderwidth=0, highlightthickness=0, padx=5, pady=5)
frame.pack(padx=30, pady=30)

# Draw the button that opens the folder picker for downloading files
open_folder = tkinter.Button(frame, text="Download files", command=click_download_files)
open_folder.grid(row=0, column=0)

Spacer1 = tkinter.Label(frame, text = "       ")
Spacer1.grid(row=0,column=1)

# Draw the button that opens the folder picker for the metadata log
open_folder = tkinter.Button(frame, text="Create metadata log", command=click_metadata_log)
open_folder.grid(row=0, column=2)

Spacer1 = tkinter.Label(frame, text = "       ")
Spacer1.grid(row=0,column=3)

# Draw the button that opens the folder picker for the readme
open_folder = tkinter.Button(frame, text="Create readme", command=click_readme)
open_folder.grid(row=0, column=4)

Spacer2 = tkinter.Label(frame, text = "       ")
Spacer2.grid(row=0,column=5)

# Draw the button that opens the folder picker for the Datacite XML
open_folder = tkinter.Button(frame, text="Create DOI XML", command=click_doi)
open_folder.grid(row=0, column=6)


# Initialize Tk window
app.mainloop()
