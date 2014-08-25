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
from poster_resources.vimeo import *
from poster_resources.flickr import *


THUMBNAIL_SIZE = 100,100
MEDIUM_SIZE = 300,300
ALLOWEDCHARS = "abcdefghijklmnopqrstuvwxyz0123456789"

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
        self.image_id = 0
    
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
        self.image_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO phoo_image_album (phoo_image_id,"
                     "phoo_album_id) VALUES (%s,%s)",(self.image_id, 1))
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
            return -1
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
    
    def __youtube(self, summary):
        '''
        Search for youtube tags and implement the right html code
        '''
        youtube_ids = get_youtube_ids(summary)
        if youtube_ids: 
            
            splittext = summary.split("\n")
            tmplines  = []
            for line in splittext:
                for yid in youtube_ids:
                    if line.find(yid) != -1 and line.startswith("[youtube]"):
                        include_more = True 
                        #Bingo, youtube ID!
                        line = get_youtube_text(yid, include_more)
                        break
                tmplines.append(line)
            summary = "\n".join(tmplines)
        return summary

    def __vimeo(self, summary):
        '''
        Search for vimeo tags and implement the right html code
        '''
        vimeo_ids = get_vimeo_ids(summary)
        if vimeo_ids: 
            splittext = summary.split("\n")
            tmplines  = []
            for line in splittext:
                for yid in vimeo_ids:
                    if line.find(yid) != -1 and line.startswith("[vimeo]"): 
                        include_more = True
                        #Bingo, vimeo ID!
                        line = get_vimeo_text(yid, include_more)
                        break
                tmplines.append(line)
            summary = "\n".join(tmplines)
        return summary
    
    def __flickr(self, summary):
        '''
        Search for flickr tags and implement the right html code
        '''
        flickr_ids = get_flickr_ids(summary)
        if flickr_ids: 
            splittext = summary.split("\n")
            tmplines  = []
            for line in splittext:
                for yid in flickr_ids:
                    if line.find(yid) != -1 and line.startswith("[flickr]"):
                        include_more = line.find('more') > -1
                        #Bingo, flickr ID!
                        line = get_flickr_text(yid, include_more)
                        break
                if isinstance(line, unicode):
                    line = str(line)
                tmplines.append(line)
            summary = "\n".join(tmplines)
        return summary
    
    def __tags(self, summary):
        '''Check for the tags keyword and returns the summary without 
        the keywords and a list of tags found'''
        lines = summary.split("\n")
        tags = []
        summary = "\n".join([k for k in lines if not k.startswith("[tags]")])
        for line in lines:
            if line.startswith("[tags]"):
                tags.extend([k.strip() for k in line.replace("[tags]","").split(",")])
                continue
        return summary, tags
    
    def link_tags(self, post_id, tags):
        '''Link the post with a category (we call it here as a tag), if the tag does not
        exist then it is created, search for tags is performed in lower case'''
        if not tags:
            return
        database = connect_to_database()
        cursor = database.cursor()
        cursor.execute("SELECT id, name FROM blog_category")
        categories = cursor.fetchall()
        for tag in tags:
            #Exists??
            matches = [k[0] for k in categories if k[1].lower() == tag.lower()]
            if not matches:
                #Add the new category:
                query = ("INSERT INTO blog_category (name, createtime, updatetime) "
                        "VALUES (%s,NOW(),NOW())")
                cursor.execute(query,(tag,))
                database.commit()
                cursor.execute("SELECT LAST_INSERT_ID()")
                matches.append(cursor.fetchone()[0])
            #link
            for match in matches:
                query = ("INSERT INTO blog_entrycat (entry_id, category_id) "
                        "VALUES (%s,%s)")
                cursor.execute(query, (post_id, match))
        database.commit()
        cursor.close()
        database.close()

    
    def new_post(self, title, summary='', content=''):
        '''
        Create a new post, returns the post ID
        @param title: Title of the post
        @param summary: Summary of the post
        @param content: content of the post
        '''
        fast_url = ""
        for char in title:
            if char not in ALLOWEDCHARS and char not in ALLOWEDCHARS.upper():
                char = "_"
            fast_url += char
        fast_url = fast_url.decode("utf8")
        database = connect_to_database()
        cursor = database.cursor()
        createtime = datetime.datetime.now()
        summary = self.__youtube(summary)
        summary = self.__vimeo(summary)
        summary = self.__flickr(summary)
        tags = []
        summary, tags = self.__tags(summary)
                    
        if summary.find("[more]") != -1:
            tmpsummary = summary.split("[more]")
            content = "".join(tmpsummary)
            summary  = tmpsummary[0]
            
        tmpsummary = ''
        for line in summary.split("\n"):    
            if line.strip():
                tmpsummary += " " + line
                continue
            tmpsummary += "\n\n"
        summary = tmpsummary.replace("\r",'')
        
        tmpcontent = ""
        for line in content.split("\n"):    
            if line.strip():
                tmpcontent += " " + line
                continue
            tmpcontent += "\n\n"
        content = tmpcontent.replace("\r",'')
        #Check if there is another title with fast_url"
        cursor.execute("SELECT 1 FROM blog WHERE fast_url=%s",(fast_url))
        append = 0
        while cursor.fetchone():
            append += 1
            tmpfasturl = "%s%d"%(fast_url,append)
            cursor.execute("SELECT 1 FROM blog WHERE fast_url=%s",(tmpfasturl))
        if append:
            fast_url = "%s%d"%(fast_url,append)
        cursor.execute('INSERT INTO blog (title, fast_url, text, summary, '
                       'user_id, createtime, publishtime, updatetime, published) '
                'VALUES (%s,%s,%s,%s,%s,NOW(),NOW(),NOW(),1 )', (title, 
                                 fast_url, 
                                 content.encode("latin1",errors="ignore"), 
                                 summary.encode("latin1",errors="ignore"), 
                                 self.get_user_id(self.sender)))
        database.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        post_id = cursor.fetchone()[0]
        self.link_tags(post_id, tags)
        cursor.close()
        database.close()
        return post_id
