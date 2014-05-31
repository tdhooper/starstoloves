Stars to Loves
==============

Migrate Spotify stars to Last.fm loves

* Runs in a Vagrant box
* Based on https://github.com/torchbox/vagrant-django-template
* Includes extra dependencies:
** libspotify and pyspotify (http://pyspotify.mopidy.com)
** lfmh (https://bitbucket.org/hauzer/lfm/)

Setup
-----
    
    1. Install Vagrant 
    2. Start vagrant
        $ vagrant up
    3. The site should be available at http://localhost:8111

The Django server will be running in a screen and can be accessed like so

    $ vagrant ssh
    $ screen -r djangoServer

For the Celery worker do

    $ vagrant ssh
    $ screen -r celeryWorker