#!/usr/bin/env python

#License (BSD)
#
#* Copyright (c) 2011, Kevin Minnick
#* All rights reserved.
#*
#* Redistribution and use in source and binary forms, with or without
#* modification, are permitted provided that the following conditions are met:
#*     * Redistributions of source code must retain the above copyright
#*       notice, this list of conditions and the following disclaimer.
#*     * Redistributions in binary form must reproduce the above copyright
#*       notice, this list of conditions and the following disclaimer in the
#*       documentation and/or other materials provided with the distribution.
#*     * Neither the name of Kevin Minnick nor the
#*       names of its contributors may be used to endorse or promote products
#*       derived from this software without specific prior written permission.
#*
#* THIS SOFTWARE IS PROVIDED BY Kevin Minnick ''AS IS'' AND ANY
#* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#* DISCLAIMED. IN NO EVENT SHALL Kevin Minnick BE LIABLE FOR ANY
#* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# This script will index all of the files stored in your cloud files account
# so they are searchable by lucene.  The script requires that you have cloudfuse
# installed and running locally.  You will also need lucene and tika installed.

# See the README file for detailed installation instructions.

import os
import os.path
from subprocess import call
import re

#constants, you should edit this section to meet your needs
class Constants(object):
  def __init__(self):
    #mount point for cloudfiles via cloudfuse
    self.root = "/root/cloudfiles"
    #root container
    self.container = ""
    #temp file storage and index
    self.tmp = "/tmp"
    #container in cloud files to store indexes
    self.cf_index_dir = "/cf_index_dir"
    #name of tika jar
    self.tika = "tika-app-1.0.jar"
    #extension for extracted txt
    self.tika_ext = ".tika.xml"
    #name of lucene app to do actual indexing
    self.index_jar = "org.apache.lucene.demo.IndexFiles"
    #list of containers to exclude from index, supports regular expressions
    self.exclude_containers = set([self.cf_index_dir, "cloudservers", ".CDN_ACCESS_LOGS", "lb_*"])
    #debug level 0=off 1=on
    self.debug_level = 0

def main():

  c = Constants()

  #make lucene directory if necessary
  cf_index_dir = c.root + c.cf_index_dir
  if(os.path.exists(cf_index_dir) == False):
    call(["mkdir", cf_index_dir])

  #loop through every file in cloud files
  for root, dirs, files in os.walk(c.root + "/" + c.container):
    for name in files:
      #full path of mounted cloud file
      src = os.path.join(root, name)
      #container name
      dir_name = src.replace(c.root, '', 1)
      dir_name = dir_name.replace("/" + name, '', 1)
      #name of extracted txt file
      tika_file = name + c.tika_ext
      #full path of location to store extracted text on cloud files
      final_dest = cf_index_dir + "/" + dir_name + "/" + tika_file

      #skip containers in the exclude list
      skip_container = False
      for container in c.exclude_containers:
        if re.search(container, dir_name):
          print "Excluding " + src
          skip_container = True
          break

      if skip_container:
        continue

      if(os.path.exists(final_dest)):
        print "Skipping " + src
        continue
      else:
        print "Indexing " + src

      dest = c.tmp + "/" + name
      
      #copy file locally
      if c.debug_level > 0:
        print "cp " + src + " " + dest
      call(["cp", src, dest])

      #strip out text
      if c.debug_level > 0:
        print "indexing file"
      tmp_file = c.tmp + "/" + tika_file
      tmp_file_handle = open(tmp_file, 'w')
      
      if c.debug_level > 0:
        print "java -jar " + c.tika + " " + dest + " > " + tmp_file
      call(["java", "-jar", c.tika, dest], stdout=tmp_file_handle)

      #make the container if necessary
      index_cont = cf_index_dir + "/" + dir_name
      if(os.path.exists(index_cont) == False):
        if c.debug_level > 0:
          print "mkdir " + index_cont
        call(["mkdir", index_cont])

      #copy txt to cloud files
      if c.debug_level > 0:
        print "cp " + tmp_file + " " + final_dest
      call(["cp", tmp_file, final_dest])

      #delete local files
      if c.debug_level > 0:
        print "deleting local files"
      call(["rm", dest])
      call(["rm", tmp_file])

  #index the files
  print "Indexing files"
  call(["java", c.index_jar, "-docs", c.root + "/" + c.cf_index_dir, "-update"])  

  return

if __name__ == '__main__':
  try:
    main()
  except EOFError:
    print "\n"
    exit()
