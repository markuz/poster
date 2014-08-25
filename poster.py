#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the Poster project
#
# Copyright (c) 2006-2009 Marco Antonio Islas Cruz
#
# Poster is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Poster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2011 Marco Antonio Islas Cruz
# @license   http://www.gnu.org/licenses/gpl.txt
import sys
import os
from poster_resources.mail import mail
from poster_resources.settings import conf_mail, SITE_URL
from poster_resources.jaws import Blog, Phoo
from poster_resources.youtube import *
from poster_resources.vimeo import *

class poster(object):
    def __init__(self):
        '''
        Constructor
        '''
        #Get mails
        c = mail(conf_mail['host'], conf_mail['port'],
                 conf_mail['username'],
                 conf_mail['password'])
        for message in c.get_unseen_mail():
            if message.get_subject().lower().startswith("upload:"):
                #handle upload only
                pass
            else: #Post this message
                self.create_post(message)
    
    def create_post(self, message):
        '''
        Handy method to create a message. Messages are all preformatted
        @param message:
        '''
        blog = Blog()
        blog.sender = message.get_from()
        if blog.get_user_id(blog.sender) == -1:
            print >> sys.stderr, "Can't work with this sender: %s"%repr(blog.sender)
            return
        post_txt = ''
        #Save images if there are any..
        imagelist = []
        if message.get_images():
            phoo = Phoo()
            phoo.sender = message.get_from()
            for filename, image in message.get_images():
                imagelist.append(phoo.add_image(image, message.get_from(),
                                                filename))
        youtube_ids  = get_youtube_ids("".join(message.get_text()))
        for yid in youtube_ids:
            phoo = Phoo()
            phoo.sender = message.get_from()
            name, data = get_youtube_thumbnail(yid)
            if message.get_text().find("[novideoimage]") > -1:
                continue
            imagelist.append(phoo.add_image(data, message.get_from(),
                                                name))
        vimeo_ids  = get_vimeo_ids("".join(message.get_text()))
        for yid in vimeo_ids:
            phoo = Phoo()
            phoo.sender = message.get_from()
            name, data = get_vimeo_thumbnail(yid)
            if message.get_text().find("[novideoimage]") > -1:
                continue
            imagelist.append(phoo.add_image(data, message.get_from(),
                                                name))
        if imagelist:
            image = imagelist[0]
            maxwidth = min(800, image.width)
            post_txt += ('<center><img src="%s/data/phoo/%s" '
                       'alt="%s" width = %d /></center>\n\n'%(SITE_URL,
                                    '/'.join((image.partial_path,image.name)),
                                                        image.title,
                                                        maxwidth))
        #Process_text.
        post_txt += "".join(message.get_text())
        lines = post_txt.split("\n")
        newlines = []
        nothumbs = False
        links = False
        continuos_empty = 0
        for line in lines:
            if not line: 
                continuous_empty += 1
            else:
                continuous_empty = 0
            if continuous_empty > 1:
                continue
            lower = line.lower().strip()
            if lower == "[nothumbs]":
                nothumbs = True
                line = ''
            elif lower == "[novideoimage]":
                line = ''
            elif lower == "[links]":
                links = True
                line = ''
            newlines.append(line)
        post_txt = "\n\n".join(newlines)
                
        #Add aditional images:
        if imagelist and len(imagelist) > 1:
            if post_txt.find("[more]") == -1 :
                post_txt += "[more]\n"
            for image in imagelist[1:]:
                if nothumbs:
                    thumb = ''
                    maxwidth = min(800, image.width)
                    size = "width = %d"%maxwidth
                    center = "<center>"
                    center_end = "</center>"
                    
                else:
                    thumb = 'thumb'
                    size = ''
                    center = ""
                    center_end = ""
                    
                if links:
                    linkstart = ("<a href='%s/index.php?photos/"
                                 "album/1/photo/%s.html'>")%(SITE_URL,
                                                             image.image_id)
                    linkend = "</a>"
                else:
                    linkstart = ''
                    linkend = ''
                    
                src = SITE_URL + '/data/phoo/%s'% '/'.join(
                                        (image.partial_path,thumb,image.name))
                
                post_txt += ("%s%s<img src='%s' alt='%s' %s />%s%s\n\n")%(center,
                              linkstart, src,image.name, size, linkend,
                              center_end)
                
        print blog.new_post(message.get_subject(), post_txt)
                
            

if __name__ == '__main__':
    p = poster()
