'''
Created on Dec 7, 2011

@author: Marco Antonio Islas Cruz
'''
import urllib
import urlparse
import json
from poster_resources.settings import flickr_settings
from poster_resources.third_party import flickr as FLICKR

#Set flickr API_KEY
FLICKR.API_KEY = flickr_settings["key"]
FLICKR.API_SECRET = flickr_settings["secret"]
FLICKR.email = flickr_settings["email"]
FLICKR.password = flickr_settings["password"]
FLICKR.AUTH = False

def get_flickr_ids(text):
    '''
    Sarch for flickr links on text.
    @param text:
    '''
    flickr_id = []
    for index, data in enumerate(text.split("\n")):
        if data.find("[flickr]")!=-1:
            data = data.replace("[flickr]", '').replace("[/flickr]",'')
            #flickr url are pretty good :-)
            split = data.strip().split("/")
            if len(split) < 6:
                continue
            #Should be somehing like 
            #http://www.flickr.com/photos/user/int_photo_id/in/whatever
            flickr_id.append(split[5])
    return flickr_id

def get_flickr_text(flickr_id, include_more = False):
    photo = FLICKR.Photo(flickr_id)
    flickrstring = ('<center>'
                 '<a href="%s" title="%s"><img src="%s" alt="%s"></a>'
                 '</center>'%(
                 photo.url, photo.title, photo.getMedium(), photo.title))
    return flickrstring

def get_flickr_thumbnail_url(flickr_id):
    '''
    Returns the url for the flickr id
    @param flickr_id:
    '''
    photo = FLICKR.Photo(flickr_id)
    return photo.getmedium()

def get_flickr_thumbnail(flickr_id):
    '''
    Return the flickr image as text/plain,
    Downloads the thumbnail for the given flickr_id
    
    NOTE: Originally, it should be better to leave the picture in flickr..
            the better if we don't use this function
    
    returns the name of the file, renamed from 0.jpg to a timestamp name, to 
    avoid file overwriting. and the data of the file.
    @param flickr_id:
    '''
    url = get_flickr_thumbnail_url(flickr_id)
    name = url.split("/")[-1]
    resource = urllib.urlopen(url)
    data  = resource.read()
    return name, data
    
        
