

# changeing those requires reprovision

node_count                = 1        # worker node count
ampq_queuename            = "hello"  # queue name

# changing this requires recreating everything from scratch
# for simplicy we gona use /24 subnet so we can jusst simply add last octet.
subnet = "172.17.177"#.0/24
zabbix_port = 8080          # port for zabbix webinterface access
rabbitmq_mgmt_port = 15672  # port for rabbitmq webinterface access

# dont change stuff below

$box = 'debian/buster64'

servers = {
  'central' => 253,         # central server
  'controller' => 254       # controller node for ansible
}

# generate nodes
nodes = {}
workers =[]

(1..node_count).each do |c|
  name = "worker#{c}"
  nodes[name] = c+1
  workers.push("worker#{c.to_s}")
end
#merge nodes
nodes.merge!(servers)

# hostvars for ansible
host_vars = {}
ansible_groups = {
  "server" => ['central'],
  "workers"  => workers,            # looks like vagrant wants to validate groups and "eats" things that would let ansible do some matching.
  "zabbix_serverss" => ['central'],
  "zabbix_servers" => ['central'],
  "ampq_servers" => ['central'],
  "all:vars" => {
    "ampq_queuename" => ampq_queuename
  }
}
Vagrant.configure("2") do |config|
  # we are disabling vbguest plugin autoupdate so it does'nt interfere with anything 
  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end
  # create vms
  nodes.each do |machine|
    name = machine[0]
    ip = "#{subnet}.#{machine[1]}"
    config.vm.define name do |node|
      node.vm.hostname = name
      # we dont need any synced stuff on nodes
      if name != "controller" 
        node.vm.synced_folder ".", "/vagrant", disabled: true
      end

      # port forwarding
      if name == "central"
        node.vm.network "forwarded_port", guest: 80, host: zabbix_port
        node.vm.network "forwarded_port", guest: 15672, host: rabbitmq_mgmt_port
      end

      node.vm.box = $box
      node.vm.network "private_network", ip: ip
      # generate ansible hostvars with paths to ssh keys
      host_vars[name] = {
        ansible_ssh_host: ip,
        ansible_ssh_private_key_file: "/vagrant/.vagrant/machines/" + name + "/virtualbox/private_key"
      }

      # we have reached controller, all other vms should be up at this stage
      # and it should be safe to provision now

      if name == "controller"
        # loop trough all nodes and grab priv keys.
        nodes.each do |mash|
          nname = mash[0]
          if nname != "controller"
            node.vm.provision :file do |file|  
              file.source       = ".vagrant/machines/" + nname + "/virtualbox/private_key"
              file.destination  = "/vagrant/.vagrant/machines/" + nname + "/virtualbox/private_key"
            end
            if Vagrant::Util::Platform.windows? then
              node.vm.provision :shell, inline: "chmod 700 /vagrant/.vagrant/machines/#{nname}/virtualbox/private_key"
            end
          end
        end
        # provisioning ansible and dependencies
        node.vm.provision :shell, inline: "apt-get update && apt-get install -y python3-pip && pip3 install ansible zabbix-api ansible"
        # provisioning everything else with ansible
        node.vm.provision :ansible_local do |ansible|
          ansible.playbook        = "playbook.yml"
          ansible.verbose         = true
          ansible.limit           = "all"
          ansible.host_vars       = host_vars
          ansible.groups          = ansible_groups
        end
      end
    end
  end
end

