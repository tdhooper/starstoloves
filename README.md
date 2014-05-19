starstoloves
============

Migrate Spotify stars to Last.fm loves

* Runs in a Vagrant box
* Based on https://github.com/torchbox/vagrant-django-template
* Includes extra dependencies:
** libspotify and pyspotify (http://pyspotify.mopidy.com)
** lfmh (https://bitbucket.org/hauzer/lfm/)

Setup
-----
    
    $ vagrant up
    $ vagrant ssh
      (then, within the SSH session:)
    ./manage.py runserver 0.0.0.0:8000

This will make the app accessible on the host machine as http://localhost:8111/ . The codebase is located on the host
machine, exported to the VM as a shared folder; code editing and Git operations will generally be done on the host.