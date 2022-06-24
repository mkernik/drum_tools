# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 11:22:36 2022

@author: kerni016
"""

import urllib.request
import math
from bs4 import BeautifulSoup
from datetime import datetime


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
        print(url + " could not be opened. (" + str(e) + ")")

    #Read in the content at the item API endpoint and get the internal id for the item
    presoup = BeautifulSoup(response, 'lxml')
    item_info = presoup.p.text
    item_dict = eval(item_info.replace('null', '"null"'))

    internal_id = item_dict["id"]
    
    bitstream_url = "https://conservancy.umn.edu/rest/items/" + str(internal_id) + "/bitstreams?limit=250"
    metadata_url = "https://conservancy.umn.edu/rest/items/" + str(internal_id) + "/metadata"


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
    metadata_log_path = outputDir + "/metadata_" + str(handle_split[1]) + "_" + str(datetime.now().strftime("%Y%m%d")) + ".txt"
    f = open(metadata_log_path,"w")
    f.write(metadata_log_template)
    f.close()