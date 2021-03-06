# -*- coding: utf-8 -*-
"""
script name:DRUM_downloadFiles.py
inputs: -DRUM handle URL (i.e. https://hdl.handle.net/11299/226188 or https://conservancy.umn.edu/handle/11299/226188)
        -directory path for where files should be downloaded
outputs: -folder named using the last 6 numbers of the submission handle
         -downloaded content files from the DRUM submission
description: This tkinter script tool creates a folder named using the last
6 numbers of the handle and downloads the content files from the
submission into that folder. Known limitation: it cannot download files that
are embargoed on the record.
last modified: June 2022
@author: kerni016 and vmcollins
"""


##import necessary modules and return a message if any are not available
try:
    import urllib.request
    from math import floor
    from math import log
    from math import pow
    from os import mkdir
    from os import path
    import tkinter.filedialog
    import tkinter.messagebox
    from tkinter import ttk
    from bs4 import BeautifulSoup

except Exception as e:
    print(e)

def convert_size(size_bytes):
    """Convert file size in bytes to a more human readable format"""
    
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(floor(log(size_bytes, 1024)))
    p = pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

#Create message box if there is an error
def show_error(text):
    tkinter.messagebox.showerror('Error', text)

#Create message box describing results of clicking a button
def show_results(text):
    tkinter.messagebox.showinfo("Results", text)

def validate_input(handle_url, outputDir):
    """
    Check that the API endpoint URL can be generated from the enter handle URL.
    Check whether a folder already exists for the submission in the selected
    target location.  If it does not, create a new folder using the unique six number
    handle for the submission.
    """    
    
    handle_url_valid = False
    outputDir_valid = False

    #Use the handle URL to construct a URL to get to the Dspace endpoint for the item
    handle_split = handle_url.split ("/") [-2:]
    end_handle = str(handle_split[1])
    handle = str(handle_split[0]) + "/" + str(handle_split[1])
    url = "https://conservancy.umn.edu/rest/handle/" + handle

    #Try to access the Dspace endpoint. Return an error message and stop if the URL cannot be opened.
    try:
        response = urllib.request.urlopen(url)
        handle_url_valid = True
    except Exception as e:
        show_error("The tool cannot access information for\n" + handle_url + ".\n Double check the handle URL.") 
        print("The API endpoint (" + url + ") could not be opened:  " + str(e))

    #Create a folder with the unique handle number of the submission. Return an error if that folder already exists.
    if handle_url_valid:
        download_path = outputDir + "/" + end_handle + "/"
        if path.isdir(download_path):
            show_error("The folder (" + download_path + ") already exists in the target location. Files will not be (re)downloaded.")
            print("The folder (" + download_path + ") already exists in the target location. Files will not be (re)downloaded.")
        else:
            try:
                mkdir(download_path)
                print("Creating directory: " + download_path)
                outputDir_valid = True
            except Exception as e:
                show_error("Error creating directory: " + download_path + " Check console for more error details.")
                print("Error creating directory: " + download_path + " (" + str(e) + ")")
    
    if handle_url_valid and outputDir_valid:
        return True


def downloadFiles (handle_url, outputDir):
    """
    Scrape information about submission files from the item bitstream API endpoint.
    Construct a download link and use it to download the files to the submission
    folder generated by the validate_input tool
    """
        
    #Use the handle URL to construct a URL to get to the Dspace endpoint for the item
    handle_split = handle_url.split ("/") [-2:]
    end_handle = str(handle_split[1]) 
    full_handle = str(handle_split[0]) + "/" + str(handle_split[1])
    url = "https://conservancy.umn.edu/rest/handle/" + full_handle
    response = urllib.request.urlopen(url)

    #Read in the content at the item API endpoint and get the internal id for the item
    presoup = BeautifulSoup(response, 'lxml')
    item_info = presoup.p.text
    item_dict = eval(item_info.replace('null', '"null"'))
    internal_id = item_dict["id"]
         
    #Use the internal ID to construct a URL to get to the Dspace endpoint for the item bitstreams. 
    #Default limit is 20 items per page. Extended to 250 to account for larger data submissions.
    bitstream_url = "https://conservancy.umn.edu/rest/items/" + str(internal_id) + "/bitstreams?limit=250"
    download_path = outputDir + "/" + end_handle + "/"
    
    #Read in the content at the bitstream API endpoint. 
    response = urllib.request.urlopen(bitstream_url)
    item_soup = BeautifulSoup(response, 'lxml')
    bitstream = item_soup.p.text
    list_bitstream = eval(bitstream.replace('null', '"null"'))

    #Create counters for number of downloaded and passed files
    downloaded_files = 0
    passed_files = 0
    
    #For each bitstream in the bundle "ORIGINAL", construct a download link and request the files
    for x in list_bitstream:
        if x['bundleName'] == "ORIGINAL":
            try:
                filename = x['name']
                #check for white spaces in bitstream filename and create an alternative link for download if found
                if ' ' in filename:
                    newfilename = filename.replace(' ', '%20')
                    sequenceId = x['sequenceId']
                    download = "https://conservancy.umn.edu/bitstream/handle/" + full_handle + "/" + newfilename + "?sequence=" + str(sequenceId) + "&isAllowed=y/"
                    print("Now downloading: " + filename + " (" + convert_size(x['sizeBytes']) + ") ...")
                    urllib.request.urlretrieve(download, (download_path + "\\" + filename))
                    print(filename + " has been downloaded")
                    downloaded_files += 1
                else:
                    sequenceId = x['sequenceId']
                    download = "https://conservancy.umn.edu/bitstream/handle/" + full_handle + "/" + filename + "?sequence=" + str(sequenceId) + "&isAllowed=y/"
                    print("Now downloading: " + filename + " (" + convert_size(x['sizeBytes']) + ") ...")
                    urllib.request.urlretrieve(download, (download_path + "\\" + filename))
                    print(filename + " has been downloaded")
                    downloaded_files += 1
            except Exception as e:
                print ("Cannot download: " + filename + ". Skipping file.  Please try downloading manually. More detail about the error: " + str(e))
                passed_files += 1
                pass
    if downloaded_files >= 1:
        show_results("Finished downloading " + str(downloaded_files) + " files from: \n" + handle_url + "\n" + str(passed_files) + " were skipped due to a download error.")
    else:
        show_results("Finished, but no files were downloaded. Check whether the files are embargoed. They must be manually downloaded.")
    
    
# Create the GUI interface
app = tkinter.Tk()
app.geometry('700x300')
app.title("DRUM Download Tools")


# Open the folder picker, create a folder in the selected location named with the handle number, and download the files.
def click_download():
    #set user feedback to display while downloading
    open_folder['text'] = "Downloading..."
    describe_text['text'] = "\n\nIf the app seems stuck, check console window for current progress!\n\n"

    #Get information provided by the user
    handle_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    
    #If the user has entered a valid handle and output directory, download files
    if handle_url and outputDir:
        valid = validate_input(handle_url, outputDir)
        if valid:
            downloadFiles(handle_url, outputDir)
    
    #If the user has not entered the necessary information, request it
    elif outputDir:
        show_error("Please enter the URL for a DRUM submission")
    elif handle_url:
        show_error("Please select an output folder")
    
    #reset user interface
    open_folder['text'] = "Download files"
    describe_text['text'] = """
    This tool creates a folder in the chosen directory named after the unique handle submission number (e.g. 226188).
    If the folder already exists, it will not download files.
    Embargoed files will be skipped.\n"""

# Create the window header
header = tkinter.Label(app, text="DRUM Download Tool!", fg="blue", font=("Cabin", 24))
header.pack(side="top", ipady=20)

# Add the descriptive text
text = tkinter.Label(app, text="""
Enter the handle for a DRUM submission
Example: https://conservancy.umn.edu/handle/11299/226188\n""")
text.pack()

# Draw box for entering the handle URL
entry = ttk.Entry(app, width = 70)
entry.pack(ipady=2)

# Add the descriptive text
describe_text = tkinter.Label(app, text="""
This tool creates a folder in the chosen directory named after the unique handle submission number (e.g. 226188).
If the folder already exists, it will not download files.
Embargoed files will be skipped.\n""")
describe_text.pack()

# Draw the button that opens the folder picker for where to create the folder/download the files
open_folder = tkinter.Button(app, text="Download files", command=click_download)
open_folder.pack(ipady=2)


# Initialize Tk window
app.mainloop()
