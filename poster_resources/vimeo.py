'''
Created on Oct 24, 2011

@author: markuz
'''
import urllib
import urlparse

def get_vimeo_ids(text):
    '''
    Sarch for vimeo links on text.
    @param text:
    '''
    vimeo_id = []
    for index, data in enumerate(text.split("\n")):
        if data.find("[vimeo]")!=-1:
            data = data.replace("[vimeo]", '').replace("[/vimeo]",'')
            #Vimeo url are pretty good :-)
            split = data.strip().split()
            if len(split) != 4:
                continue
            vimeo_id.append(split[-1])
    return vimeo_id

def get_vimeo_text(vimeo_id, include_more = False):
    vimeostring = ("\n[more]\n"
                 '<center>'
                 '<iframe src="http://player.vimeo.com/video/%s?title=0'
                 '&amp;byline=0&amp;portrait=0" width="800" height="450" '
                 'frameborder="0" webkitAllowFullScreen mozallowfullscreen '
                 'allowFullScreen></iframe>'%vimeo_id)
    return vimeostring

def get_vimeo_thumbnail_url(vimeo_id):
    '''
    Returns the url for the vimeo id
    @param vimeo_id:
    '''
    data = ''
    try:
        op = urllib.urlopen("http://vimeo.com/api/v2/video/%s.json"%vimeo_id)
        data = op.read()
        op.close()
    except:
        pass
    url = json.loads(data)[0]['thumbnail_large']
    return url

def get_vimeo_thumbnail(vimeo_id):
    '''
    Return the vimeo image as text/plain,
    Downloads the thumbnail for the given vimeo_id
    
    returns the name of the file, renamed from 0.jpg to a timestamp name, to 
    avoid file overwriting. and the data of the file.
    @param vimeo_id:
    '''
    url = get_vimeo_thumbnail_url(vimeo_id)
    name = url.split("/")[-1]
    resource = urllib.urlopen(url)
    data  = resource.read()
    return name, data
    
        
