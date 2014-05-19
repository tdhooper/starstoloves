# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
	# Base box to build off, and download URL for when it doesn't exist on the user's system already
	config.vm.box = "precise32"
	config.vm.box_url = "http://files.vagrantup.com/precise32.box"

	# As an alternative to precise32, VMs can be built from the 'django-base' box as defined at
	# https://github.com/torchbox/vagrant-django-base , which has more of the necessary server config
	# baked in and thus takes less time to initialise. To go down this route, you will need to build
	# and host django-base.box yourself, and substitute your own URL below.
	#config.vm.box = "django-base-v2.1"
	#config.vm.box_url = "http://vmimages.torchbox.com/django-base-v2.1.box"  # Torchbox-internal URL to django-base.box
	
	# Boot with a GUI so you can see the screen. (Default is headless)
	# config.vm.boot_mode = :gui
	
	# Assign this VM to a host only network IP, allowing you to access it
	# via the IP.
	# config.vm.network "33.33.33.10"
	
	# Forward a port from the guest to the host, which allows for outside
	# computers to access the VM, whereas host only networking does not.
	config.vm.network "forwarded_port", guest: 8000, host: 8111

	# Share an additional folder to the guest VM
	config.vm.synced_folder ".", "/home/vagrant/starstoloves"
	
	# Enable provisioning with a shell script.
	config.vm.provision :shell, :path => "etc/install/install.sh", :args => "starstoloves"
end
