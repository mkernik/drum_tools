# -*- coding: utf-8 -*-
"""
script name:DRUM_downloadFiles_Dspace7.py

inputs: -DRUM URL, handle, or DOI (i.e. https://conservancy.umn.edu/items/ad4695da-3d2a-4f74-8097-8c68418fba33, https://hdl.handle.net/11299/226188, or https://doi.org/10.13020/ksjb-4w36)
        -directory path for where files should be downloaded
outputs: -folder named using the last 6 numbers of the submission handle
         -downloaded content files from the DRUM submission

description: This tkinter script tool creates a folder named using the last
6 numbers of the handle and downloads the content files from the
submission into that folder. Known limitation: it cannot download files that
are embargoed on the record.

Last modified: July 2024
Original script: June 2022
@authors: Melinda Kernik(kerni016) and Valerie Collins(vmcollins)

"""

##import necessary modules and return a message if any are not available
try:
    import urllib.request
    import requests
    import time
    from math import floor
    from math import log
    from math import pow
    from os import mkdir
    from os import path
    import tkinter.filedialog
    import tkinter.messagebox
    from tkinter import ttk
    
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

def validate_input(link_url, outputDir):
    """
    Check that the API endpoint URL can be generated from the enter handle URL.
    Check whether a folder already exists for the submission in the selected
    target location.  If it does not, create a new folder using the unique six number
    handle for the submission.
    """ 
    
    link_url_valid = False
    outputDir_valid = False    
    
    print ("Requesting information from DRUM API...")    
    
    #Take the input entered by the notebook user and extract the item_uuid
    drum_url_split = link_url.split ("/") [-2:]
    item_uuid_test = str(drum_url_split[0])
    if item_uuid_test == "items":
      item_uuid = str(drum_url_split[1])
    else:
      resolved_url = requests.get(link_url)
      r_new_url = resolved_url.url
      drum_url_split = r_new_url.split ("/") [-2:]
      item_uuid = str(drum_url_split[1])
    
    #Construct the link to the API endpoint
    item_api_url = "https://conservancy.umn.edu/server/api/core/items/" + item_uuid
    
    #Try to access the Dspace endpoint. Return an error message and stop if the URL cannot be opened.
    try:
        response = requests.get(item_api_url)
        link_url_valid = True
        itemData = response.json()
        handle_uri = itemData['metadata']['dc.identifier.uri'][0]['value']
        handle_split = handle_uri.split ("/") [-2:]
        #print (handle_split[1])
    except Exception as e:
        show_error("The tool cannot access information. Double check the URL.") 
        print("The API endpoint (" + item_api_url + ") could not be opened:  " + str(e))
    
    ###Replaced by file specific level embargo check? 
    #Check whether all associated files are embargoed
    # try:
    #     response = requests.get(item_api_url + "/accessStatus")
    #     accessData = response.json()
    #     status = accessData['status']
    #     print (status)
    # except Exception as e:
    #     print("The API endpoint (" + item_api_url + ") could not be opened:  " + str(e))
        
    #Create a folder with the unique handle number of the submission. Return an error if that folder already exists.
    if link_url_valid:       
        download_path = outputDir + "/" + handle_split[1] + "/"
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
    
    if link_url_valid and outputDir_valid:
        return True, item_api_url, download_path
        #return True, item_api_url, download_path, status


def downloadFiles (link_url, item_api_url, download_path):
    """
    Scrape information about the deposited files from the item bitstream API endpoint.
    Construct a download link and use it to download the files to the submission
    folder generated by the validate_input tool
    """ 
    response = requests.get(item_api_url)
    itemData = response.json()
    
    bundles_url = itemData['_links']['bundles']['href']
    bundles_response = requests.get(bundles_url)
    bundlesData = bundles_response.json()
    
    for x in range(len(bundlesData['_embedded']['bundles'])):
        if bundlesData['_embedded']['bundles'][x]['name'] == "ORIGINAL":
            bitstreams_url = bundlesData['_embedded']['bundles'][x]['_links']['bitstreams']['href']
    #print (bitstreams_url)
    
    bits_response = requests.get(bitstreams_url)
    bitstreamsData = bits_response.json()
    
    downloaded_files = 0
    passed_files = 0
    embargoed_files = 0
    for page in range(bitstreamsData['page']['totalPages']):
        next_url = bitstreams_url + "?page=" + str(page)
        response = requests.get(next_url)
        bitstreamsDataExtra = response.json()
        for x in range(len(bitstreamsDataExtra['_embedded']['bitstreams'])):
            filename = bitstreamsDataExtra['_embedded']['bitstreams'][x]['name']
            identifier = bitstreamsDataExtra['_embedded']['bitstreams'][x]['id']
            filesize = convert_size(bitstreamsDataExtra['_embedded']['bitstreams'][x]['sizeBytes'])
            download = "https://conservancy.umn.edu/bitstream/" + identifier + "/download"        
                        
            try:
                print("Now downloading: " + filename + " (" + filesize + ") ...")
                # Check for the contentType of the file in the header. If text/html, check whether if there is text from the log-in screen (indicating it is embargoed)
                response = requests.head(download)
                contentType = response.headers['content-type']
                if 'text/html' in contentType:
                    response = requests.get(download)
                    if "<title>University Digital Conservancy :: Login" in response.text:
                        print ("Check if " + filename + " is embargoed.")
                        embargoed_files += 1
                    else:
                        urllib.request.urlretrieve(download, (download_path + "//" + filename))
                        print(filename + " has been downloaded")
                        downloaded_files += 1
                        time.sleep(1)
                else:
                    urllib.request.urlretrieve(download, (download_path + "//" + filename))
                    print(filename + " has been downloaded")
                    downloaded_files += 1
                    time.sleep(1)
            except Exception as e:
                print ("Cannot download: " + filename + ". Skipping file.  Please try downloading manually. More detail about the error: " + str(e))
                passed_files += 1
                pass
    if downloaded_files >= 1:
        show_results("Finished downloading " + str(downloaded_files) + " files from: \n" + link_url + "\n" + str(embargoed_files) + " were skipped due to embargo.\n" + str(passed_files) + " were skipped due to a download error.")
    else:
        show_results("Finished, but no files were downloaded.")    
        
       
# Create the GUI interface
app = tkinter.Tk()
app.geometry('700x300')
app.title("DRUM Download Tools Dspace7")


# Open the folder picker, create a folder in the selected location named with the handle number, and download the files.
def click_download():
    #set user feedback to display while downloading
    open_folder['text'] = "Downloading..."
    describe_text['text'] = "\nIf the app seems stuck, check console window for current progress!\n"

    #Get information provided by the user
    link_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    
    #If the user has entered a valid handle and output directory, download files
    if link_url and outputDir:
        valid, item_api_url, download_path = validate_input(link_url, outputDir)
        if valid:
            downloadFiles(link_url, item_api_url, download_path)
        #valid, item_api_url, download_path, status = validate_input(link_url, outputDir)
        ###Replaced with file specific embargo check?
        # if status == 'open.access':
        #     if valid:
        #         downloadFiles(link_url, item_api_url, download_path)
        # elif status == 'embargo':    
        #     show_error("Some files connected to this data deposit are under embargo. A folder was created, but the files must be manually downloaded.")
    
    #If the user has not entered the necessary information, request it
    elif outputDir:
        show_error("Please enter the URL for a DRUM submission")
    elif link_url:
        show_error("Please select an output folder")
    
    #reset user interface
    open_folder['text'] = "Download files"
    describe_text['text'] = """
    This tool creates a folder in the chosen directory named after the unique handle submission number (e.g. 226188).
    If the folder already exists, it will not download files.
    Embargoed files will be skipped.\n"""

# Create the window header
header = tkinter.Label(app, text="DRUM Download Tool (Dspace7)", fg="blue", font=("Cabin", 24))
header.pack(side="top", ipady=20)

# Add the descriptive text
text = tkinter.Label(app, text="""
Enter the link or handle for a DRUM submission
Example: https://conservancy.umn.edu/items/940c6197-486b-437c-96ca-cca9b4534dfa\n""")
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
