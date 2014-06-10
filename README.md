Stars to Loves
==============

Migrate Spotify stars to Last.fm loves.

Setup
-----

You will need a Spotify premium account, Spotify application key, and a Last.fm API application key and secret.

A Spotify application key can be obtained from https://devaccount.spotify.com/my-account/keys/, and a Last.fm application key and secret from http://www.last.fm/api/account/create.

1. Rename `starstoloves/starstoloves/settings/local.py.example` to `local.py`
 * Add your Last.fm key and secret to `local.py`
 * Add your Spotify premium account username and password to `local.py`
2. Save the binary version of your Spotify application key to `starstoloves/starstoloves/spotify_appkey.key`
3. Install Vagrant http://www.vagrantup.com/
4. Start vagrant:
    
        $ vagrant up
        
5. The site should be available at [http://localhost:8111/](http://localhost:8111)

Debugging
---------

The Django server will be running in a screen and can be accessed like so:

    $ vagrant ssh
    $ screen -r djangoServer

For the Celery worker do:

    $ vagrant ssh
    $ screen -r celeryWorker
