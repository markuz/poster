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
'''
Created on Dec 14, 2011

@author: markuz
'''

from optparse import OptionParser

parser = OptionParser()
parser.add_option('-d','--debug', help='Run in debug mode', 
                  action='store_true', dest='debug')
parser.add_option('-a','--all-messages',dest='all_messages',
                  action='store_true',
                  help=('Get all messages, not only the unseen'))

options, args = parser.parse_args()