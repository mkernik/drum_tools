# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 15:45:29 2022

@author: kerni016
"""

import urllib.request
from os import mkdir
from bs4 import BeautifulSoup



def download_files (handle_url, outputDir):
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
    end_handle = handle_split[1] 
    
    #Create a folder with the unique handle number of the submission. Return an error if that folder already exists.
    try:
        download_path = outputDir + "\\" + end_handle + "\\" 
        mkdir(download_path)
        print("Creating directory: " + download_path)
    except Exception as e:
        print("Error creating directory (" + str(e) + ")")
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
                    
                    download = "https://conservancy.umn.edu/bitstream/handle/" + handle + "/" + newfilename + "?sequence=" + str(sequenceId) + "&isAllowed=y/"
                    print (download)
                    urllib.request.urlretrieve(download, (download_path + "\\" + filename))
                else:
                    download = "https://conservancy.umn.edu/bitstream/handle/" + handle + "/" + newfilename + "?sequence=" + str(sequenceId) + "&isAllowed=y/"
                    print (download)
                    urllib.request.urlretrieve(download, (download_path + "\\" + filename))
            except:
                print ("Cannot download: " + filename + ". There may be spaces in the file name.  Please try downloading manually." )
                pass