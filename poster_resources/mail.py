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

import re
import imaplib
import email
from email.header import decode_header
from poster_resources.database import connect_to_database
from poster_resources.options import options



pattern_ecre = re.compile(r'((=\?.*?\?[qb]\?).*\?=)', re.VERBOSE | re.IGNORECASE | re.MULTILINE)

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
        headers = decode_header(header)
        header = []
        for text,encoding in headers:
            text = text.decode(encoding or 'ascii')
            header.append(text)
        return " ".join(header)
    
    def get_from(self):
        '''
        Return the from header
        '''
        return self.decode_header(self.message['from'])


    def decodeSafely(self, x):
        match = pattern_ecre.search(x)
        if not match:
            return x
        string, encoding = match.groups()
        stringBefore, string, stringAfter = x.partition(string)
        return self.decode_header(" ".join((stringBefore, string, stringAfter)))
    
    def get_subject(self):
        '''
        Return the subject of the message
        '''
        result1 = self.decodeSafely(self.message["subject"])
        return result1
            
    def walk(self):
        '''
        Return the text of the message
        '''
        self.text_list = []
        self.image_list = []
        for part in self.message.walk():
            type = part.get_content_type()
            if type.startswith("text/plain"):
                self.text_list.append(part.get_payload(decode=True))
            elif type.startswith("image/"):
                filename = part.get_filename()
                payload  = part.get_payload(decode=True)
                self.image_list.append((filename, payload))
                
    def get_text(self):
        return "\n".join(self.text_list).decode("utf-8")
    
    def get_images(self):
        return self.image_list

class mail(object):
    '''
    This class offers a way to get new emails from an IMAP server
    '''
    def __init__(self, host, port,  username, password):
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
        query_type = 'UNSEEN'
        if options.all_messages:
            query_type = 'ALL'
        typ, data = M.search(None, query_type)
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
