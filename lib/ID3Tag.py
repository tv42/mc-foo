#!/usr/bin/python
# Downloaded from http://home.earthlink.net/~joecotellese/  --Tv
##    ID3Tag.py - a python class for reading ID3v1 tags
##    part of the Python MP3 library
##    Copyright (C) 2000  Joe Cotellese
##
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program; if not, write to the Free Software
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys, os, tempfile, shutil
from threading import *

class ID3Tag :
    """
    This class provides methods for accessing the ID3 tags in
    the MP3 file format.

    The ID3 tag is an extremely simple (and limited) way of binding
    information about a particular MP3 file with the file itself.

    The information is placed at the end of the file. It is 128 bytes
    long. This 128 bytes are broken into various fields. Each field
    is 0 padded.

    The structure is as follows:

    Field       Length      Offset
    TAG         3           0-2
    Songname    30          3-32
    Artist      30          33-62
    Album       30          63-92
    Year        4           93-96
    Comment     30          97-126
    Genre       1           127

    Descriptions:
    TAG - this is a three byte header at the beginning of the structure.
    It denotes that there is indeed an ID3 tag attached to this file.
    Songname - the name of the song.
    Artist - the person or group that sang the song
    Album - the album this song is recorded on.
    Comment - a field that is used to enter extra information about the song
    Genre - a byte value which corresponds to an offset in a table of genres.
    This table is shown below.

    """
    
    # The genre list, this list is split into two. The original
    # MP3 genres and the WinAMP specfic genres. I don't currently
    # know how many players support the WinAMP extensions.
    #

    #original MP3 genres
    MP3_genre_list = ['Blues','Classic Rock','Country','Dance',
                      'Disco','Funk','Grunge','Hip-Hop',
                      'Jazz','Metal','New Age','Oldies',
                      'Other','Pop','R&B','Rap',
                      'Reggae',
                      'Rock','Techno','Industrial','Alternative',
                      'Ska','Death Metal','Pranks','Soundtrack',
                      'Euro-Techno','Ambient','Trip-Hop','Vocal',
                      'Jazz+Funk','Fusion','Trance','Classical',
                      'Instrumental','Acid','House','Game',
                      'Sound Clip','Gospel','Noise','AlternRock',
                      'Bass','Soul','Punk','Space',
                      'Meditative','Instrumental Pop','Instrumental Rock','Ethnic',
                      'Gothic','Darkwave','Techno-Industrial','Electronic',
                      'Pop-Folk','Eurodance','Dream','Southern Rock',
                      'Comedy','Cult','Gangsta','Top 40',
                      'Christian Rap','Pop/Funk','Jungle','Native American',
                      'Cabaret','New Wave','Psychadelic',
                      'Rave','Showtunes','Trailer','Lo-Fi',
                      'Tribal','Acid Punk','Acid Jazz','Polka',
                      'Retro','Musical','Rock & Roll','Hard Rock']

    #others defined by WinAMP folks
    WINAMP_genre_list = ['Folk','Folk-Rock','National Folk','Swing',
                         'Fast Fusion','Bebob','Latin','Revival',
                         'Celtic','Bluegrass','Avantgarde','Gothic Rock',
                         'Progressive Rock','Psychedelic Rock','Symphonic Rock','Slow Rock',
                         'Big Band','Chorus','Easy Listening','Acoustic','Humour',
                         'Speech','Chanson','Opera','Chamber Music',
                         'Sonata','Symphony','Booty Bass','Primus',
                         'Porn Groove','Satire','Slow Jam','Club',
                         'Tango','Samba','Folklore','Ballad',
                         'Power Ballad','Rhythmic Soul','Freestyle','Duet',
                         'Punk Rock','Drum Solo','Acapella','Euro-House',
                         'Dance Hall']

    #misc found in KDE MP3 Tag Editor
    OTHER_genre_list = ['Goa', 'Drum & Bass', 'Club-House', 'Hardcore',
                        'Terror', 'Indie', 'BritPop', 'NegerPunk',
                        'Polsk Punk', 'Beat']
                  
    def __init__(self, file):

        #Initialize our variables now because
        #we want known data in the fields if we
        #are going to write to a file.
        self.m_Title=""
        self.m_Artist=""
        self.m_Album=""
        self.m_Year=""
        self.m_Comment=""
        self.m_Genre=0xFF
        self.dirty = 0  
        self.filename=file
        self.f_lock = Lock()
        
        return


#public interfaces

## The functions that begin with theXXX are the accessor functions
## they basicaly just return the member function of the accessor name.
## Note that for these to be of any use, you must first either Read() the
## file or set the members with the mutators (below).

    def theTitle(self):
        """
        This function will return the title of the MP3
        file.
        """                
        return self.m_Title

    def theArtist(self):
        """
        This function will return the artist of the MP3 file
        """
        return self.m_Artist

    def theAlbum(self):
        """
        This function returns the album
        """
        return self.m_Album
    
    def theYear(self):
        """
        This function returns the year as a string
        """
        return self.m_Year

    def theGenre(self):
        """
        This function returns the genre string of the MP3 file. It will
        perform the lookup into the genre table.
        """
        list = self.MP3_genre_list + self.WINAMP_genre_list + self.OTHER_genre_list
        if self.m_Genre<len(list):
            return list[self.m_Genre]
        else:
            return "Unknown"

    def theComment(self):
        """
        This function returns the comment field of the MP3 file
        """
        return self.m_Comment

## These functions are the object mutators, they are used to set the individual
## members of the object. When any of the members are are set, a dirty flag is
## set to tell the object that the items need to be committed to a file.

    def Title(self,name):
        """
        This function sets the song name of the file
        """
        self.dirty=1
        self.m_Title = name

    def Artist(self,name):
        """
        This function sets the artist name of the file
        """
        self.dirty=1
        self.m_Artist = name

    def Album(self,name):
        self.dirty=1
        self.m_Album = name
        
    def Year(self,year):
        """
        This function takes a string representing the year that the
        song was originally released.
        """
        self.dirty=1
        self.m_Year = year

    def Genre(self,genre):
        """
        This function take a string representing the genre of the song.
        It then converts it to the proper value in the lookup table.
        If the genre is unknown then the genre is set to FF (self,unknown)
        """

        self.dirty=1

        list = self.MP3_genre_list + self.WINAMP_genre_list

        for x in range(0, len(list)):
            if list[x] == genre:
                self.m_Genre = x
                break
        
    def Comment(self, comment):
        """
        This function takes a string and is usually some extra information
        about the song.
        """
        self.dirty=1
        self.m_Comment=comment

#
# File manipulation member functions
#
    def Remove(self):
        """
        This function strips the ID3 tag from a file.
        """
        #seialize access to the file
        self.f_lock.acquire()


        #try to read in the ID3 header
        fp = open(self.filename, "rb")        
        fp.seek(-128, 2) #2 specifies to seek from the end of the file
        temp = fp.read(3)

        if temp == "TAG":
            #We have an ID3 header, let's take it out.

            pos = fp.tell() - 3 #because we're past the TAG header            
            fp.seek(0)

            #create the temp file
            tmp_name =  tempfile.mktemp()

            op = open(tmp_name, "wb")
            op.write(fp.read(pos))

            fp.close()
            op.close()

            #copy the temp file to the original file
            shutil.copyfile(tmp_name, self.filename)
            os.remove(tmp_name)
        else:
            fp.close()
            
        self.f_lock.release()

        
    def Commit(self):
        """
        This function writes an MP3 tag to the file
        """
        
        #only do this if the file has changed.
        if not self.dirty:
            print "not dirty"
            return


        self.Remove()
        
        self.f_lock.acquire()

        fp = open (self.filename, "a+")
        
        #go to the end of the file
        fp.seek(-0,2)

        #end write the ID3 tags
        fp.write("TAG")
        fp.write(self.PrepField(self.m_Title, 30))
        fp.write(self.PrepField(self.m_Artist,30))
        fp.write(self.PrepField(self.m_Album,30))
        fp.write(self.PrepField(self.m_Year,4))
        fp.write(self.PrepField(self.m_Comment, 30))

        #is this the best way to do this? I want to just write a
        #byte of data.
        fp.write(chr(self.m_Genre))

        fp.close()

        self.dirty = 0
        
        self.f_lock.release()
        
    def Read(self):
        """
        Read in an MP3 file and put the information into
        the ID3 tag structure. ID3 tags are then returned
        by the appropriate accessor methods.
        """
        #seialize access to the file
        self.f_lock.acquire()

        #read in the file    
        fp = open(self.filename, "rb")

        fp.seek(-128, 2) #2 specifies to seek from the end of the file
        temp = fp.read(3)
        if temp != "TAG":
            raise StandardError, "No TAG header found in MP3 file:" + self.filename

        self.m_Title = self.RemovePadding(fp,30)
        self.m_Artist= self.RemovePadding(fp,30)
        self.m_Album = self.RemovePadding(fp,30)
        self.m_Year=self.RemovePadding(fp,4)
        self.m_Comment=self.RemovePadding(fp,30)
        self.m_Genre=ord(fp.read(1)) # we need to convert this to an integer

        fp.close()
        self.f_lock.release()
        return

#private functions
    def RemovePadding (self, file, field_len):
        """
        This remove the 0x00 padding from an MP3 field.
        """
        string=""
        for x in range (0, field_len):
            x = file.read(1)
            if ord(x) !=0:
                string = string + x

        return string

    def PrepField(self, value, field_len):
        """
        The ID3 tag format has specific requirements for
        a field length. This function ensure the field
        meets these requirements by padding or truncating
        the field as necessary.
        """

        if len(value) == field_len:
            return value
        
        if len(value)>field_len:
            return value[:field_len]
        
        string = value
        for p in range(len(value), field_len):
            string = string + chr(0x00)

        return string
        
#the test harness
def test():

    if len(sys.argv)<2:
        print "ID3 Test harnass requires a filename."
        return

    filename = sys.argv[1]

    #read in the tag
    tag=ID3Tag(filename)
  
    try:
        tag.Remove()
        tag.Remove()
        
        tag.Read()
        print tag.theTitle()
        print tag.theArtist()
        print tag.theAlbum()
        print tag.theYear()
        print tag.theGenre()
        print tag.theComment()
        
        #write test
        tag.Title("Close to the Edge. I Total Time of Change, Total Mass retain")
        tag.Artist("Yes")
        tag.Album("Close to the Edge")
        tag.Year("1972")
        tag.Genre("Rock")
        tag.Comment("This track is the first on the disk")

        tag.Commit()
            
            
        tag.Read()
        print tag.theTitle()
        print tag.theArtist()
        print tag.theAlbum()
        print tag.theYear()
        print tag.theGenre()
        print tag.theComment()

    except StandardError, e:
        print e

if __name__=='__main__':
    test()
