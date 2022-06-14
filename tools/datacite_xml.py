# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 11:31:55 2022

@author: kerni016
"""
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime


def datacite_xml(handle_url, outputDir):
    
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
    
    metadata_url = "https://conservancy.umn.edu/rest/items/" + str(internal_id) + "/metadata"
    
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
    schema_log_path = outputDir + "/doi_metadata_" + str(handle_split[1]) + ".xml"
    f = open(schema_log_path,"w") 
    f.write(datacite_schema)
    f.close()
