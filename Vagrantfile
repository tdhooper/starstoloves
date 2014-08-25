# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    # Every Vagrant virtual environment requires a box to build off of.
    config.vm.box = "urban/trusty64-node"

    # Create a forwarded port mapping which allows access to a specific port
    # within the machine from a port on the host machine. In the example below,
    # accessing "localhost:8080" will access port 80 on the guest machine.
    config.vm.network "forwarded_port", guest: 8000, host: 8111

    # Share an additional folder to the guest VM
    config.vm.synced_folder ".", "/home/vagrant/starstoloves"

    config.vm.provision :shell, :privileged => false, :path => "etc/install/install.sh", :args => "starstoloves"
    config.vm.provision :shell, :privileged => false, :path => "etc/install/start.sh", :args => "starstoloves", :run => "always"
end
