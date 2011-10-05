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

import MySQLdb

from poster_resources.settings import database, phoo_path
from poster_resources.database import connect_to_database


THUMBNAIL_SIZE = 100,100
MEDIUM_SIZE = 300,300

class Phoo(object):
    '''
    This class allows the interaction with the Phoo gadget
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def add_image(self, data, user_id, filename, title='', description=''):
        '''
        Create a file from data (data must be what the image is in text, 
        as if it were read in binary mode), using filename, title and 
        description
        @param user_id: 
        @param filename:
        @param title:
        @param description:
        @param data:
        '''
        self.create_images(filename, data)
        fname = os.path.join(fullpath, filename)
        database = connect_to_database()
        cursor = databse.cursor()
        if os.path.exists(fname):
            #File exists. we don't need to save it anymore.
            cursor.execute("SELECT image_id FROM phoo_image WHERE "
                         "filename = %s",(filename,))
            result = cursor.fetchone()
            if result:
                return result[0],filename
        #Save the object in database.
        if not title:
            title = ".".join(filename.split('.')[:-1])
        cursor.execute("INSERT INTO phoo_image (user_id, filename, title, "
                     "description VALUES (%s,%s,%s,%s)",
                     (user_id, filename, title or filename, description))
        cursor.commit()
        image_id = cursor.execute("SELECT LAST_INSERT_ID()")
        cursor.execute("INSERT INTO phoo_image_album (phoo_image_id"
                     "phoo_album_id) VALUES (%s,%s)",(image_id, 1))
        cursor.commit()
        cursor.close()
        database.close()
        return image_id, filename
    
    def create_images(self, filename, data):
        #Get the year, month and day to create the directory where the picture
        #is going to be store
        now = datetime.datetime.now()
        directory = "%d_%d_%d"%(now.year, now.month, now.day)
        fullpath = os.path.join(phoo_path, directory)
        thumbpath = os.path.join(phoo_path, directory, 'thumb')
        mediumpath = os.path.join(phoo_path, directory, 'medium')
        for path in (fullpath, thumbpath, mediumpath):
             if not os.path.exists(path):
                 os.makedirs(path)
        #We save the normal image, no modifications need to be made
        fname = os.path.join(fullpath, filename)
        fobj = open(fname, 'wb')
        fobj.write(data)
        fobj.close()
        #Saving medium image and thumbnail
        thumb = os.path.join(thumbpath, filename)
        medium = os.path.join(mediumpath, filename)
        for cname, sizes in ((thumb, THUMBNAIL_SIZE, medium, MEDIUM_SIZE)):
            image = Image.open(fname)
            image.thumbnail(sizes)
            image.save(cname)
            
        

class Blog(object):
    '''
    This class allows the interaction with the Blog gadget
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
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
        cursor.execute('INSERT INTO blog (title, fast_url, text, summary) '
                'VALUES (%s,%s,%s,%s)', (title, fast_url, content, summary))
        cursor.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        post_id = cursor.fetchone()[0]
        cursor.close()
        database.close()
        return post_id