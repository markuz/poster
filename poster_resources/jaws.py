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
import MySQLdb
import datetime
from poster_resources.settings import database, phoo_path
from poster_resources.database import connect_to_database
from PIL import Image
from poster_resources.youtube import *


THUMBNAIL_SIZE = 100,100
MEDIUM_SIZE = 300,300

class JawsImage(object):
    '''
    This class represents a Jaws Phoo Image.
    '''
    def __init__(self, name, data):
        '''
        Constructor
        @params name: Name of the file to be saved
        @params data: string with the data.
        '''
        self.data = data
        self.name = name
        self.user_id = 1
        self.title = ''
        self.description = ''
    
    def save(self):
        '''
        Save the image in the file system and add it to the database
        '''
        user_id = self.user_id
        self.create_images()
        fname = os.path.join(self.fullpath, self.name)
        database = connect_to_database()
        cursor = database.cursor()
        if os.path.exists(fname):
            #File exists. we don't need to save it anymore.
            cursor.execute("SELECT id FROM phoo_image WHERE "
                         "filename = %s",(self.name,))
            result = cursor.fetchone()
            if result:
                return 
        #Save the object in database.
        if not self.title:
            self.title = ".".join(self.name.split('.')[:-1])
        cursor.execute("INSERT INTO phoo_image (user_id, filename, title, "
                     "description) VALUES (%s,%s,%s,%s)",
                     (self.user_id, os.path.join(self.partial_path, self.name), 
                      self.title, self.description))
        database.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        image_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO phoo_image_album (phoo_image_id,"
                     "phoo_album_id) VALUES (%s,%s)",(image_id, 1))
        database.commit()
        cursor.close()
        database.close()
   
    def create_images(self):
        #Get the year, month and day to create the directory where the picture
        #is going to be store
        data = self.data 
        filename = self.name 
        title = self.title 
        description = self.description
        now = datetime.datetime.now()
        directory = "%d_%d_%d"%(now.year, now.month, now.day)
        self.partial_path = directory
        self.fullpath = os.path.join(phoo_path, directory)
        self.thumbpath = os.path.join(phoo_path, directory, 'thumb')
        self.mediumpath = os.path.join(phoo_path, directory, 'medium')
        for path in (self.fullpath, self.thumbpath, self.mediumpath):
             if not os.path.exists(path):
                 os.makedirs(path)
        #We save the normal image, no modifications need to be made
        fname = os.path.join(self.fullpath, filename)
        fobj = open(fname, 'wb')
        fobj.write(data)
        fobj.close()
        image = Image.open(fname)
        self.width, self.height = image.size
        #Saving medium image and thumbnail
        thumb = os.path.join(self.thumbpath, filename)
        medium = os.path.join(self.mediumpath, filename)
        for cname, sizes in ((thumb, THUMBNAIL_SIZE), (medium, MEDIUM_SIZE)):
            image = Image.open(fname)
            image.thumbnail(sizes)
            image.save(cname)


class JawsBase (object):
    def get_user_id(self,sender):
        '''
        Return the user id of the email address, or 1 if no one is found
        @param sender:
        '''
        database = connect_to_database()
        cursor = database.cursor()
        start = sender.find("<") or 0
        end = sender.find(">") or (len(sender) -1 )
        sender = sender[start + 1 :end]
        cursor.execute('SELECT id FROM users WHERE email = %s',(sender, ))
        result = cursor.fetchone()
        if not result:
            return 1
        return int(result[0])
        

class Phoo(JawsBase):
    '''
    This class allows the interaction with the Phoo gadget
    '''
    def __init__(self):
        '''
        Constructor
        '''
        JawsBase.__init__(self)
    
    def add_image(self, data, sender, filename, title='', description=''):
        '''
        Create a file from data (data must be what the image is in text, 
        as if it were read in binary mode), using filename, title and 
        description
        
        returns JawsImage Object
        '''
        #Create a new JawsImage object
        object = JawsImage(filename, data)
        object.title = title
        object.description = description
        object.user_id = self.get_user_id(sender)
        object.save()
        object.create_images()
        return object
        
class Blog(JawsBase):
    '''
    This class allows the interaction with the Blog gadget
    '''
    def __init__(self):
        '''
        Constructor
        '''
        JawsBase.__init__(self)
    
    def new_post(self, title, summary='', content=''):
        '''
        Create a new post, returns the post ID
        @param title: Title of the post
        @param summary: Summary of the post
        @param content: content of the post
        '''
        fast_url = title.replace(' ','_')
        database = connect_to_database()
        cursor = database.cursor()
        createtime = datetime.datetime.now()
        #Handle youtube links. This is a hack more than good implemented stuff
        youtube_ids = get_youtube_ids(summary)
        if youtube_ids: 
            include_more = True
            splittext = summary.split("\n")
            tmplines  = []
            for line in splittext:
                print repr(youtube_ids)
                for yid in youtube_ids:
                    if line.find(yid) != -1 and line.find(["[youtube]"]) != -1: 
                        #Bingo, youtube ID!
                        line = get_youtube_text(yid, include_more)
                        include_more = False
                        break
                tmplines.append(line)
            summary = "\n".join(tmplines)
        
        if summary.find("[more]") != -1:
            tmpsummary = summary.split("[more]")
            content = "".join(tmpsummary)
            summary  = tmpsummary[0]
            
            
        cursor.execute('INSERT INTO blog (title, fast_url, text, summary, '
                       'user_id, createtime, publishtime, published) '
                'VALUES (%s,%s,%s,%s,%s,%s,%s,1 )', (title, fast_url, content, summary,
                                            self.get_user_id(self.sender),
                                            createtime, createtime))
        database.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        post_id = cursor.fetchone()[0]
        cursor.close()
        database.close()
        return post_id