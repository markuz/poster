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
import os
from poster_resources.mail import mail
from poster_resources.settings import conf_mail, SITE_URL
from poster_resources.jaws import Blog, Phoo

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
            print "".center(80,'=')
            print message.get_from()
            print message.get_subject()
            print message.get_text()
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
        post_txt = ''
        #Save images if there are any..
        imagelist = []
        if message.get_images():
            phoo = Phoo()
            phoo.sender = message.get_from()
            for filename, image in message.get_images():
                imagelist.append(phoo.add_image(image, message.get_from(),
                                                filename))
        if imagelist:
            image = imagelist[0]
            maxwidth = min(800, image.width)
            post_txt += ('<center><img src="%s/%s" '
                       'alt="%s" width = %d /></center>\n\n'%(SITE_URL,
                                    os.path.join(image.partial_path,image.name),
                                                        image.title,
                                                        maxwidth))
        #Process_text.
        # TODO: Handle youtube links
        post_txt += "".join(message.get_text())
        
        #Add aditional images:
        if imagelist and len(imagelist) > 1:
            for image in imagelist[1:]:
                post_txt += "<img src='%s/%s' alt='%s' />"%(SITE_URL,
                         os.path.join(image.partial_path,'thumb',image.name),
                                                         image.title)
                
        blog = Blog()
        blog.sender = message.get_from()
        print blog.new_post(message.get_subject(), post_txt)
                
            

if __name__ == '__main__':
    p = poster()