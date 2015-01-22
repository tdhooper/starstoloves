Stars to Loves
==============

Migrate Spotify stars to Last.fm loves.

Setup
-----

1. You will need Last.fm and Spotify accounts, with an API application created for each
 * http://www.last.fm/api/account/create
 * https://developer.spotify.com/my-applications
2. Rename `starstoloves/starstoloves/settings/local.py.example` to `local.py`
 * Add your Last.fm application key and secret
 * Add your Spotify application client_id and client_secret
3. Install Vagrant http://www.vagrantup.com
4. Start vagrant:
    
        $ vagrant up
        
5. The site should be available at [http://localhost:8111](http://localhost:8111)

Debugging
---------

The Django server will be running in a screen and can be accessed like so:

    $ vagrant ssh
    $ screen -r djangoServer

For the Celery worker do:

    $ vagrant ssh
    $ screen -r celeryWorker

Running tests
-------------

Run tests like so:

    $ vagrant ssh
    $ workon starstoloves
    $ cd /vagrant
    $ py.test
