'''
Created on Oct 24, 2011

@author: markuz
'''
import urllib
import urlparse

def get_youtube_ids(text):
    '''
    Sarch for youtube links on text.
    @param text:
    '''
    youtube_id = []
    for index, data in enumerate(text.split("\n")):
        if data.find("[youtube]")!=-1:
            data = data.replace("[youtube]", '').replace("[/youtube]",'')
            parseresult = urlparse.urlparse(data.strip())
            querys = [k.split("=") for k in parseresult.query.split("&")]
            if not querys:
                continue
            params = [k for k in map(lambda x: [None, x[1]][x[0]=='v'], querys) if k]
            if params: 
                youtube_id.extend(params)
    return [k for k in youtube_id if k]

def get_youtube_text(youtube_id, include_more = False):
    more = ['','\n[more]\n'][include_more]
    youtubestring = ("%s"
                 '<div class="video-contenedor">'
                 '<iframe width="800" height="437" '
                 'src="http://www.youtube.com/embed/%s?hd=1"'
                 ' frameborder="0" allowfullscreen></iframe>'
                 '</div>'%(more, youtube_id))
    return youtubestring

def get_youtube_thumbnail_url(youtube_id):
    '''
    Returns the url for the youtube id
    @param youtube_id:
    '''
    return "http://img.youtube.com/vi/%s/0.jpg"%youtube_id

def get_youtube_thumbnail(youtube_id):
    '''
    Return the youtube image as text/plain,
    Downloads the thumbnail for the given youtube_id
    
    returns the name of the file, renamed from 0.jpg to a timestamp name, to 
    avoid file overwriting. and the data of the file.
    @param youtube_id:
    '''
    url = get_youtube_thumbnail_url(youtube_id)
    resource = urllib.urlopen(url)
    data  = resource.read()
    return "%s.jpg"%youtube_id, data
    
        
