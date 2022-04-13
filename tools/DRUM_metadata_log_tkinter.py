# -*- coding: utf-8 -*-
"""
script name:DRUM_metadata_log_tkinter.py

inputs: -DRUM handle URL (i.e. https://hdl.handle.net/11299/226188 or https://conservancy.umn.edu/handle/11299/226188)
        -Directory path for the metadata log
output: text file metadata log ("metadata_log_[last 6 numbers of the handle]_")

description: This tkinter script tool generates a metadata log based on the 
information entered by researchers during the submission process to the Data 
Repository for the University of Minnesota (DRUM) and the original files uploaded.

last modified: April 2022
author: Melinda Kernik
"""

##import necessary modules and return a message if any are not available
try:
    import urllib
    #import sys
    import math
    import tkinter
    import tkinter.filedialog
    import tkinter.messagebox
    from tkinter import ttk
    #from tkinter import *
    from bs4 import BeautifulSoup
    from datetime import datetime

except Exception as e:
    print(e)

def show_error(text): 
    tkinter.messagebox.showerror('Error', text)

def show_results(text):
    tkinter.messagebox.showinfo("Results", text)    

def convert_size(size_bytes):
    """Convert file size in bytes to a more human readable format"""

    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def metadata_log(handle_url, outputDir):
    
    #Use the handle URL to construct a URL to get to the Dspace endpoint for the item  
    handle_split = handle_url.split ("/") [-2:]
    handle = str(handle_split[0]) + "/" + str(handle_split[1])
    url = "https://conservancy.umn.edu/rest/handle/" + handle
    
    #Try to access the Dspace endpoint. Return an error message and exit the script if the URL cannot be opened.
    try:
        response = urllib.request.urlopen(url)
    except Exception as e:
        show_error(url + " could not be opened. (" + str(e) + ")")
    
    #Read in the content at the endpoint and get the internal id for the item
    presoup = BeautifulSoup(response, 'lxml')
    item_info = presoup.p.text
    item_dict = eval(item_info.replace('null', '"null"'))
    
    internal_id = item_dict["id"]
    
    
    ###Get item bitstream information from the submission
    
    #Read in the content at the bitstream endpoint. Default limit is 20 items per page.  
    #Extended to 250 to account for larger data submissions.
    url = "https://conservancy.umn.edu/rest/items/" + str(internal_id) + "/bitstreams?limit=250"
    response = urllib.request.urlopen(url)
    item_soup = BeautifulSoup(response, 'lxml')
    bitstream = item_soup.p.text
    list_bitstream = eval(bitstream.replace('null', '"null"'))
    
    #Create the item bitstream section of the log
    bitstream_string = ""
    for x in list_bitstream:
        if x['bundleName'] == "ORIGINAL":
            bitstream_string += (x['name'] + " (" + convert_size(x['sizeBytes']) + ")\n")
    
    
    ###Get metadata from the submission
    #Use the internal id to create the URL endpoint needed to access the metadata
    url = "https://conservancy.umn.edu/rest/items/" + str(internal_id) + "/metadata"
    
    #Read in the content at the metadata endpoint
    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response, 'lxml')
    metadata = soup.p.string
    list_metadata = eval(metadata.replace('null', '"null"'))
    
    #Create the original metadata section of the log
    metadata_string = ""
    for x in range(len(list_metadata)):
        metadata_string += list_metadata[x]['key'] + " : " + list_metadata[x]['value'] +"\n"
    
    
    ###Add the bitstream and metadata lists to the template metadata log text
    metadata_log_template = "Metadata log created: " + str(datetime.now().strftime("%Y-%m-%d")) + """
\n*************************************************
Files received:
*************************************************\n""" + bitstream_string + """
*************************************************
Changes made to files:
*************************************************

**************************************************
Metadata Changes
**************************************************

**************************************************
Correspondence Notes
**************************************************

*************************************************
Other issues
*************************************************

*************************************************
Original Metadata from Author:
*************************************************\n"""  + metadata_string
    
    
    #Write the metadata log to a text file
    metadata_log_path = outputDir + "/metadata_" + str(handle_split[1]) + "_" + str(datetime.now().strftime("%Y%m%d")) + ".txt"
    f = open(metadata_log_path,"w") 
    f.write(metadata_log_template)
    f.close()
    show_results("Finished creating metadata file for: " + handle_url)


# Create the Tkinter interface.
app = tkinter.Tk()
app.geometry('600x300')
app.title("Create Metadata Log")


# Open the file picker and send the selected files to the metadata_log() function.
def clicked():
    handle_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    if handle_url and outputDir:
        metadata_log(handle_url, outputDir)
    elif outputDir:
        show_error("Please enter the URL for a DRUM submission")
    elif handle_url:
        show_error("Please select an output folder")


# Create the window header.
header = tkinter.Label(app, text="Create a Metadata Log File!", fg="blue", font=("Cabin", 24))
header.pack(side="top", ipady=20)

# Add the descriptive text.
text = tkinter.Label(app, text="""
Enter the handle for a DRUM submission
Example: https://conservancy.umn.edu/handle/11299/226188\n""")
text.pack()

# Draw box for entering the handle URL
entry = ttk.Entry(app, width = 70)
entry.pack(ipady=2)
                     
# Draw the button that opens the file picker.
open_folder = tkinter.Button(app, text="Choose folder for output", command=clicked)
open_folder.pack(ipady=2, side = "bottom", expand = "True")


# Initialize Tk window.
app.mainloop()