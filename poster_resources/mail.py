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

import imaplib
import email
from email.header import decode_header
from poster_resources.database import connect_to_database

class Message(object):
    # TODO: Create properties
    '''
    This class represents a message. We don't care of all about this message
    we just care about title, and files.
    ''' 
    def __init__(self, message):
        '''
        Receives a email.Message object, from where a more flexible
        representation will be done.
        @param message:
        '''
        self.message = message
        self.walk()
    
    def decode_header(self, header):
        text, encoding = decode_header(header)[0]
        if encoding:
            return text.decode(encoding)
        return unicode(text)
    
    def get_from(self):
        '''
        Return the from header
        '''
        return self.decode_header(self.message['from'])
    
    def get_subject(self):
        '''
        Return the subject of the message
        '''
        return self.decode_header(self.message['subject'])
    
    def walk(self):
        '''
        Return the text of the message
        '''
        self.text_list = []
        self.image_list = []
        for part in self.message.walk():
            type = part.get_content_type()
            if type.startswith("text/"):
                self.text_list.append(part.get_payload(decode=True))
            elif type.startswith("image/"):
                filename = part.get_filename()
                payload  = part.get_payload(decode=True)
                self.image_list.append((filename, payload))
                
    def get_text(self):
        return self.text_list
    
    def get_images(self):
        return self.image_list
    
    def get_user_id(self):
        '''
        Return the user_id 
        '''
        database = connect_to_database

class mail(object):
    '''
    This class offers a way to get new emails from an IMAP server
    '''
    def __init__(self, host, username, password):
        '''
        Constructor
        '''
        self.host = host
        self.username = username
        self.password = password
        
    
    def get_unseen_mail(self):
        '''
        Return instances of unseen email in Message objects.
        '''
        M = imaplib.IMAP4_SSL(self.host)
        M.login(self.username, self.password)
        M.select()
        typ, data = M.search(None, 'UNSEEN')
        c = 0
        messages = []
        for num in data[0].split():
            typ, data = M.fetch(num, '(RFC822)')
            c +=1
            print c
            message = Message(email.message_from_string(data[0][1]))
            #Create message object
            messages.append(message)
        M.close()
        M.logout()
        return messages
