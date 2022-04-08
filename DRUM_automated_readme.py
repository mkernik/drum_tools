# -*- coding: utf-8 -*-
"""
script name:DRUM_automated_readme.py

inputs: DRUM handle URL (i.e. https://hdl.handle.net/11299/226188 or https://conservancy.umn.edu/handle/11299/226188)
        Directory path for the readme
output: text file readme ("Readme_[last 6 numbers of the handle]")

description: This script generates a readme from the information entered by
researchers during the submission process to the Data Repository for the
University of Minnesota (DRUM). It is based on a readme template originally
developed at Cornell Univeristy. 

last modified: March 2022
author: Melinda Kernik
"""
##import necessary modules and return a message if any are not available
try:
    import urllib
    import sys
    from bs4 import BeautifulSoup
    from string import Template
    from datetime import datetime

except Exception as e:
    print(e)
 

#Get the handle url and the output folder path for the readme 
args = sys.argv
handle_url = args[1]
report_directory = args[2]


#Use the handle URL to construct a URL to get to the Dspace endpoint for the item  
handle_split = handle_url.split ("/") [-2:]
handle = str(handle_split[0]) + "/" + str(handle_split[1])
url = "https://conservancy.umn.edu/rest/handle/" + handle

#Try to access the Dspace endpoint. Return an error message and exit the script if the URL cannot be opened.
try:
    response = urllib.request.urlopen(url)
except Exception as e:
    print (url + " could not be opened. (" + str(e) + ")")
    raise SystemExit(0)

#Read in the content at the endpoint and get the internal id for the item
presoup = BeautifulSoup(response, 'lxml')
item_info = presoup.p.text
item_dict = eval(item_info.replace('null', '"null"'))

internal_id = item_dict["id"]

#Use the internal id to create the URL endpoint needed to access the metadata
url = "https://conservancy.umn.edu/rest/items/" + str(internal_id) + "/metadata"


###Get metadata from the submission

#Read in the content at the metadata endpoint
response = urllib.request.urlopen(url)
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
url = "https://conservancy.umn.edu/rest/items/" + str(internal_id) + "/bitstreams?limit=250"
response = urllib.request.urlopen(url)
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
    data_specific_string += """-----------------------------------------
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
readme_path = report_directory + "Readme_" + str(handle_split[1]) + ".txt"
f = open(readme_path,"w") 
f.write(readme_full_string)
f.close()
