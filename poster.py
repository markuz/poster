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
from poster_resources.mail import mail
from poster_resources.settings import mail as conf_mail

class poster(object):
    def __init__(self):
        '''
        Constructor
        '''
        #Get mails
        c = mail("%s:%d"%(conf_mail['host'], conf_mail['port']),
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
        #Save images if there are any..
        imagelist = []
        if message.get_images():
            phoo = Phoo()
            for image in message.get_images():
                imagelist.append(phoo.add_image(image))
            

if __name__ == '__main__':
    p = poster()