#!/usr/bin/env python

from distutils.core import setup

setup(name="mc-foo",
      version="0.0.4",
      description="an advanced, learning, mp3 jukebox",
      long_description="""
MC Foo is an advanced, adaptive and learning mp3 jukebox server.

  -continuous music playing
  -learns what music you like and dislike
  -no static playlists; uses a playqueue you can view and alter
  -can be controlled from any hosts and even with 
   infrared remote controllers
  -allows multiple user/preference profiles,
   according to whose listening and his or her mood

Note that MC Foo is in the early stages of development, and not
everything works yet.
""",
      author="Tommi Virtanen",
      author_email="tv@debian.org",
      url="http://mc-foo.sourceforge.net/",
      licence="GNU GPL",
      
      package_dir={"": "lib"},
      packages=[
    "McFoo", "McFoo.backend",
    "McFoo.commands", "McFoo.gui", "McFoo.server",
    "twisted.tap",
    ],
      scripts=["bin/mc-foo", "libbin/turntable"],
      )
