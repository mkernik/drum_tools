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
    import urllib.request
    import math
    from os import mkdir
    import tkinter.filedialog
    import tkinter.messagebox
    from tkinter import LabelFrame
    from tkinter import ttk
    from bs4 import BeautifulSoup
    from string import Template
    from datetime import datetime

except Exception as e:
    print(e)

#Create message box if there is an error
def show_error(text):
    tkinter.messagebox.showerror('Error', text)

#Create message box describing results of clicking a button
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


def get_urls(handle_url):

    #Use the handle URL to construct a URL to get to the Dspace endpoint for the item
    handle_split = handle_url.split ("/") [-2:]
    handle = str(handle_split[0]) + "/" + str(handle_split[1])
    url = "https://conservancy.umn.edu/rest/handle/" + handle

    #Try to access the Dspace endpoint. Return an error message and exit the script if the URL cannot be opened.
    try:
        response = urllib.request.urlopen(url)
    except Exception as e:
        show_error(url + " could not be opened. (" + str(e) + ")")

    #Read in the content at the item API endpoint and get the internal id for the item
    presoup = BeautifulSoup(response, 'lxml')
    item_info = presoup.p.text
    item_dict = eval(item_info.replace('null', '"null"'))

    internal_id = item_dict["id"]
    
    bitstream_url = "https://conservancy.umn.edu/rest/items/" + str(internal_id) + "/bitstreams?limit=250"
    metadata_url = "https://conservancy.umn.edu/rest/items/" + str(internal_id) + "/metadata"
    return handle, handle_split[1], bitstream_url, metadata_url


def download_files (handle_url, outputDir):
    full_handle, end_handle, bitstream_url, metadata_url = get_urls(handle_url)
    
    #Create a folder with the unique handle number of the submission. Return an error if that folder already exists.
    try:
        download_path = outputDir + "\\" + end_handle + "\\" 
        mkdir(download_path)
        print("Creating directory: " + download_path)
    except Exception as e:
        show_error("Error creating directory (" + str(e) + ")")
        #print ("Folder (" + download_path + ") already exists.")
    
    
    #Read in the content at the bitstream API endpoint. Default limit is 20 items per page.
    #Extended to 250 to account for larger data submissions.
    response = urllib.request.urlopen(bitstream_url)
    item_soup = BeautifulSoup(response, 'lxml')
    bitstream = item_soup.p.text
    list_bitstream = eval(bitstream.replace('null', '"null"'))
    
    #For each bitstream in the bundle "ORIGINAL", construct a download link and request the files    
    for x in list_bitstream:
        if x['bundleName'] == "ORIGINAL":
            try:
                filename = x['name']
                sequenceId = x['sequenceId']
                #check for white spaces in bitstream filename & replace if needed
                if ' ' in filename:
                    newfilename = filename.replace(' ', '%20')
                    print("New filename: " + newfilename)
                    download = "https://conservancy.umn.edu/bitstream/handle/" + full_handle + "/" + newfilename + "?sequence=" + str(sequenceId) + "&isAllowed=y/"
                    print (download)
                    urllib.request.urlretrieve(download, (download_path + "\\" + filename))
                else:
                    download = "https://conservancy.umn.edu/bitstream/handle/" + full_handle + "/" + filename + "?sequence=" + str(sequenceId) + "&isAllowed=y/"
                    print (download)
                    urllib.request.urlretrieve(download, (download_path + "\\" + filename))
            except:
                print ("Cannot download: " + filename + ". There may be spaces in the file name.  Please try downloading manually." )
                pass
    show_results("Finished downloading files for: " + handle_url)

def metadata_log(handle_url, outputDir):

    ###Get API endpoint urls based on the submission handle
    full_handle, end_handle, bitstream_url, metadata_url = get_urls(handle_url)

    #Read in the content at the bitstream API endpoint. Default limit is 20 items per page.
    #Extended to 250 to account for larger data submissions.
    response = urllib.request.urlopen(bitstream_url)
    item_soup = BeautifulSoup(response, 'lxml')
    bitstream = item_soup.p.text
    list_bitstream = eval(bitstream.replace('null', '"null"'))

    #Create the item bitstream section of the log
    bitstream_string = ""
    for x in list_bitstream:
        if x['bundleName'] == "ORIGINAL":
            bitstream_string += (x['name'] + " (" + convert_size(x['sizeBytes']) + ")\n")


    #Read in the content at the metadata endpoint
    response = urllib.request.urlopen(metadata_url)
    soup = BeautifulSoup(response, 'lxml')
    metadata = soup.p.string
    list_metadata = eval(metadata.replace('null', '"null"'))

    #Create the original metadata section of the log
    metadata_string = ""
    for x in range(len(list_metadata)):
        metadata_string += list_metadata[x]['key'] + " : " + list_metadata[x]['value'] +"\n"
        #Create variables for a few specific metadata elements (title and handle) to use in the log header
        if list_metadata[x]['key']=='dc.title':
            title = list_metadata[x]['value']
        if list_metadata[x]['key']=='dc.identifier.uri':
            handle_uri = list_metadata[x]['value']    

    ###Add the bitstream and metadata lists to the template metadata log text
    metadata_log_template = "Curation log for: " + title + """
Handle: """ + handle_uri + """
Corresponding researcher:
Curator:
Metadata log created: """ + str(datetime.now().strftime("%Y-%m-%d")) + """
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
    metadata_log_path = outputDir + "/metadata_" + str(end_handle) + "_" + str(datetime.now().strftime("%Y%m%d")) + ".txt"
    f = open(metadata_log_path,"w")
    f.write(metadata_log_template)
    f.close()
    show_results("Finished creating metadata file for: " + handle_url)



def automated_readme (handle_url, outputDir):
    
    ###Get API endpoint urls based on the submission handle
    full_handle, end_handle, bitstream_url, metadata_url = get_urls(handle_url)

    #Read in the content at the metadata endpoint
    response = urllib.request.urlopen(metadata_url)
    soup = BeautifulSoup(response, 'lxml')
    metadata = soup.p.string
    list_metadata = eval(metadata.replace('null', '"null"'))

    #Create an dictionary to be filled with metadata values from the submission
    metadata_dict = {'readme_date': str(datetime.now().strftime("%Y-%m-%d")),
                     'title':"",'date_published':"", "authors":"", "date_collected":"",
                     "spatial":"", "abstract": "", "license_info":"", "publications":"",
                     "funding":"", 'file_list':""}

    #Create lists and dictionaries to hold multi-valued metadata elements or values
    #that need to be edited before being added to the dictionary
    authors_list = []
    referenceby = []
    funders = []
    rights_dict = {}
    date_collected_dict = {}

    #For each metadata field in Dspace, check if it is something to be included in the readme.
    #If it is, add it to the metadata dictionary or to a list for further processing.
    for x in range(len(list_metadata)):
        ##General information
        if list_metadata[x]['key'] == 'dc.title':
            metadata_dict ['title'] = list_metadata[x]['value']

        if list_metadata[x]['key'] == 'dc.contributor.author':
            authors_list.append(list_metadata[x]['value'])

        if list_metadata[x]['key'] == 'dc.contributor.contactname':
            contact_name = list_metadata[x]['value']

        if list_metadata[x]['key'] == 'dc.contributor.contactemail':
            contact_email = list_metadata[x]['value']

        #Split the date field and use only YYYYMMDD, not exact time
        if list_metadata[x]['key'] == 'dc.date.available':
            date_split = list_metadata[x]['value'].split("T")
            metadata_dict ['date_published'] = date_split[0]

        if list_metadata[x]['key'] == 'dc.date.collectedbegin':
            date_collected_dict['begin'] = list_metadata[x]['value']
        if list_metadata[x]['key'] == 'dc.date.collectedend':
            date_collected_dict['end'] = list_metadata[x]['value']

        if list_metadata[x]['key'] == 'dc.coverage.spatial':
            metadata_dict ['spatial'] = list_metadata[x]['value']

        if list_metadata[x]['key'] == 'dc.description.sponsorship':
            funders.append(list_metadata[x]['value'])

        if list_metadata[x]['key'] == 'dc.description.abstract':
            metadata_dict ['abstract'] = list_metadata[x]['value']

        #Sharing/Access Information
        #Remove formatting from dc.rights field before adding it to the metadata dictionary
        if list_metadata[x]['key'] == 'dc.rights':
            rights_dict['rights'] = list_metadata[x]['value'].replace('\r\n', " ")
        if list_metadata[x]['key'] == 'dc.rights.uri':
            rights_dict['rights_url'] = list_metadata[x]['value']

        if list_metadata[x]['key'] == 'dc.relation.isreferencedby':
            referenceby.append(list_metadata[x]['value'])


    ###Format multi-valued metadata elements to be added to the metadata dictionary
    author_string = ""
    for author in authors_list:
        #Rearrange author name to be First Last instead of Last, First
        author_split = author.split (",") [:]
        author_firstLast = author_split[1] + " " + author_split[0]
        #If the author is the contact person, add their email address. If not, leave email blank.
        if author == contact_name:
            author_string += "\n\tName: " + author_firstLast + "\n\tInstitution:\n\tAddress:\n\tEmail: " + contact_email + "\n\tID:\n\n"
        else:
            author_string += "\n\tName: " + author_firstLast + "\n\tInstitution:\n\tAddress:\n\tEmail:\n\tID:\n\n"
    metadata_dict ['authors'] = author_string

    funders_string = ""
    for funder in funders:
        funders_string += "\t" + funder + "\n"
    metadata_dict ['funding'] = funders_string

    publications_string = ""
    for item in referenceby:
        publications_string += item + "\n\n"
    metadata_dict ['publications'] = publications_string


    ## Add together multiple Dspace fields to be used in one section of the readme
    if date_collected_dict:
        metadata_dict ['date_collected'] = str(date_collected_dict['begin']) + " to " + str(date_collected_dict['end'])

    if rights_dict:
        rights_string = rights_dict['rights'] + " (" + rights_dict["rights_url"] + ")"
        metadata_dict ['license_info'] = rights_string


    ###Get item bitstream information from the submission

    #Read in the content at the bitstream endpoint. Default limit is 20 items per page.
    #Extended to 250 to account for larger data submissions.
    response = urllib.request.urlopen(bitstream_url)
    item_soup = BeautifulSoup(response, 'lxml')
    bitstream = item_soup.p.text
    list_bitstream = eval(bitstream.replace('null', '"null"'))

    #Create the "File List" section of the readme and add it to the metadata dictionary
    file_list_string = "File List\n\n"
    for x in list_bitstream:
        if x['bundleName'] == "ORIGINAL":
            file_list_string += ("\tFilename: " + x['name'] +" \n\tShort description:\n\n")
    metadata_dict ['file_list'] = file_list_string


    ###Insert metadata elements from the submission into the template readme text
    readme_template = Template(
"""This readme.txt file was generated on ${readme_date} by <Name>\n
-------------------
GENERAL INFORMATION
-------------------\n
1. Title of Dataset: ${title}\n
2. Author Information\n\n${authors}
3. Date published or finalized for release: ${date_published}\n\n
4. Date of data collection (single date, range, approximate date): ${date_collected}\n\n
5. Geographic location of data collection (where was data collected?): ${spatial}\n\n
6. Information about funding sources that supported the collection of the data:\n${funding}\n
7. Overview of the data (abstract):\n${abstract}\n\n\n\n
--------------------------
SHARING/ACCESS INFORMATION
--------------------------\n
1. Licenses/restrictions placed on the data: ${license_info}\n
2. Links to publications that cite or use the data:\n${publications}
3. Was data derived from another source?
\tIf yes, list source(s):\n
4. Terms of Use: Data Repository for the U of Minnesota (DRUM) By using these files, users agree to the Terms of Use. https://conservancy.umn.edu/pages/drum/policies/#terms-of-use\n\n\n\n
---------------------
DATA & FILE OVERVIEW
---------------------\n
${file_list}\n
2. Relationship between files:\n\n
--------------------------
METHODOLOGICAL INFORMATION
--------------------------\n
1. Description of methods used for collection/generation of data:\n\n
2. Methods for processing the data: <describe how the submitted data were generated from the raw or collected data>\n\n
3. Instrument- or software-specific information needed to interpret the data:\n\n
4. Standards and calibration information, if appropriate:\n\n
5. Environmental/experimental conditions:\n\n
6. Describe any quality-assurance procedures performed on the data:\n\n
7. People involved with sample collection, processing, analysis and/or submission:\n\n\n\n""")

    #Replace variables in the template with the information from the metadata dictionary
    readme_string = readme_template.substitute(metadata_dict)


    ###Add a data_specific section to the readme for each spreadsheet file
    #Make a list of all "Original" bitstream items with ".csv" or ".xlsx" in the name
    spreadsheets = []
    data_specific_string = ""
    for x in list_bitstream:
        if x['bundleName'] == "ORIGINAL":
            if ".csv" in x['name']:
                spreadsheets.append(x['name'])
            #Will pick up a range of Excel formats including .xls, .xlsx, and .xlsm
            if ".xls" in x['name']:
                spreadsheets.append(x['name'])

    #If there are no files with .csv or .xls extensions in the submission, add a
    #placeholder "[FILENAME]" so that there will be one example section
    if not spreadsheets:
        spreadsheets.append("[FILENAME]")

    for item in spreadsheets:
        data_specific_string += """
-----------------------------------------
DATA-SPECIFIC INFORMATION FOR: """ + item + """\n-----------------------------------------\n
1. Number of variables:\n
2. Number of cases/rows:\n
3. Missing data codes:\n
\tCode/symbol\tDefinition
\tCode/symbol\tDefinition\n
4. Variable List\n
\tA. Name: <variable name>
\t   Description: <description of the variable>
\t\tValue labels if appropriate\n
\tB. Name: <variable name>
\t   Description: <description of the variable>
\t\tValue labels if appropriate\n\n\n\n"""

    #Add the data-specific section(s) onto the end of the readme
    readme_full_string = readme_string + data_specific_string

    #Write the readme to a text file
    readme_path = outputDir + "/readme_" + str(end_handle) + ".txt"
    f = open(readme_path,"w")
    f.write(readme_full_string)
    f.close()
    show_results("Finished creating readme for: " + handle_url)

def datacite_xml(handle_url, outputDir):
    
    ###Get API endpoint urls based on the submission handle
    full_handle, end_handle, bitstream_url, metadata_url = get_urls(handle_url)
    
    #Read in the content at the metadata endpoint
    response = urllib.request.urlopen(metadata_url)
    soup = BeautifulSoup(response, 'lxml')
    metadata = soup.p.string
    list_metadata = eval(metadata.replace('null', '"null"'))
    
    
    #Create a list to hold the multi-valued metadata element "author"
    authors_list = []
    
    #For each metadata field in Dspace, check if it is something to be included in the XML.
    #If it is, save it to a variable.
    for x in range(len(list_metadata)):
        ##General information
        if list_metadata[x]['key'] == 'dc.title':
            title = list_metadata[x]['value']
    
        if list_metadata[x]['key'] == 'dc.contributor.author':
            authors_list.append(list_metadata[x]['value'])
    
        if list_metadata[x]['key'] == 'dc.description.abstract':
            abstract = list_metadata[x]['value']
    
    ### Format multi-valued metadata element "author" to be added to the XML
    author_string = ""
    for author in authors_list:
        #Split up author name
        author_split = author.split (", ") [:]
        author_first = author_split[1]
        author_last = author_split[0].strip()
        #loop through authors and append each new XML <creator> block to author_string
        author_string += """
        <creator>
            <creatorName nameType="Personal">""" + author + """</creatorName>
            <givenName>""" + author_first + """</givenname>
            <familyName>""" + author_last + """</familyname>
        </creator>"""


#create beginning of XML file before the <creator> block
    datacite_schema = """<?xml version="1.0" encoding="UTF-8"?>
<resource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://datacite.org/schema/kernel-4" xsi:schemaLocation="http://datacite.org/schema/kernel-4 https://schema.datacite.org/meta/kernel-4.4/metadata.xsd">
    <identifier identifierType="DOI"></identifier>
    <creators> """ + author_string + """
    </creators>
    <titles>
        <title>""" + title + """</title>
    </titles>
    <publisher>Data Repository for the University of Minnesota (DRUM)</publisher>
    <publicationYear>""" + str(datetime.now().strftime("%Y")) + """</publicationYear>
    <resourceType resourceTypeGeneral="Dataset"/>
    <sizes/>
    <formats/>
    <version/>
    <descriptions>
        <description descriptionType="Abstract">""" + abstract + """</description>
    </descriptions>
</resource>"""

    #Write the schema to an xml file
    schema_log_path = outputDir + "/doi_metadata_" + str(end_handle) + ".xml"
    f = open(schema_log_path,"w") 
    f.write(datacite_schema)
    f.close()
    show_results("Finished creating DataCite DOI metadata for: " + handle_url)  
    
    
# Create the GUI interface
app = tkinter.Tk()
app.geometry('600x300')
app.title("DRUM Tools")


# Open the folder picker and send selected information to the metadata_log() function.
def click_download_files():
    handle_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    if handle_url and outputDir:
        download_files(handle_url, outputDir)
    elif outputDir:
        show_error("Please enter the URL for a DRUM submission")
    elif handle_url:
        show_error("Please select an output folder")

def click_metadata_log():
    handle_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    if handle_url and outputDir:
        metadata_log(handle_url, outputDir)
    elif outputDir:
        show_error("Please enter the URL for a DRUM submission")
    elif handle_url:
        show_error("Please select an output folder")

# Open the folder picker and send selected information to automated_readme() function
def click_readme():
    handle_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    if handle_url and outputDir:
        automated_readme(handle_url, outputDir)
    elif outputDir:
        show_error("Please enter the URL for a DRUM submission")
    elif handle_url:
        show_error("Please select an output folder")

# Open the folder picker and send selected information to datacite_xml() function
def click_doi():
    handle_url = entry.get()
    outputDir = tkinter.filedialog.askdirectory()
    if handle_url and outputDir:
        datacite_xml(handle_url, outputDir)
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
