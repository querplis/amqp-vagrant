# install

* install virtualbox https://www.virtualbox.org/wiki/Downloads
* install vagrant https://www.vagrantup.com/downloads
* git clone https://github.com/querplis/amqp-vagrant.git
* vagrant up

# environment
## provisioning
vagrant up will bring up:
* controller node with ansible provisioned.
* central node with zabbix server, zabbix-agent, rabbitmq and publisher/clogger apps.
* worker node(s) with  zabbix-agent and consumer service/app.
* all vm's that have zabbix-agent installed will have them added to zabbix server.
* at the very end of provisioning it will run clogger to trigger monitoring alert.

## zabbix templates/groups/macros
  We set_fact zabbix_tamplate, zabbix_groups, zabbix_hostmacros in zabbix_agent, that makes those lists "global", accessible through whole playbook.  
  zabbix-template.* roles append to those lists  
  zabbix-host role  consumes those lists, which, at this point, contains lists of templates/groups/hostvars and lets us dynamicaly generate lists of templates.

## network
We are going to use /24 subnet. For simplicity we will define variable containing first three octets so that we can just add last octet when generatig node ips.  
Subnet can be changed by changing subnet variable , default one is :
```
subnet = "172.17.177"
```
After this change enviroment has to be recreated by:
```
vagrant destroy -f && vagrant up
```

# services

## zabbix
URL: http://127.0.0.1:8080  
username: Admin  
password: zabbix  

forwarded zabbix port can be changed by changing zabbix_port variable in Vagrantfile,
after this change enviroment has to be recreated by:
```
vagrant destroy -f && vagrant up
```
## rabbitmq

URL: http://127.0.0.1:15672/  
username: guest  
password: guest  
forwarded rabbitmq managment port can be changed by cganging rabbitmq_mgmt_port variable in Vagrantfile,
after this change enviroment has to be recreated by:
```
vagrant destroy -f && vagrant up
```

# apps

## publisher

Central node will have publisher.py app installed at /var/lib/ampq_app/publisher.py.  
publisher.py accepts 1 argument as payload.  
To run it manually:
```
vagrant ssh central
sudo -u app -i
./publisher.py <payload>
```

## clogger
Central node also has clog.sh script installed at /var/lib/ampq_app/clog.sh, 
clogger will try to calculate how many nodes there are and call publisher.py
with 20 as argument enough times to trigger monitoring alert.

Every provision will run this script, to disable it comment clog play in playbook.yml.

to run clogger manualy:
```
vagrant ssh central
sudo -u app -i
./clog.sh
```

## consumer 
Every worker node when provisioned will have consumer.py app installed at /var/lib/ampq_app/consumer.py, which will consume messages from queue.  
If message is integer it will sleep that many seconds.  
Consumer app is installed as systemd service , but can be run manualy 

to stop systemd service:
```
vagrant ssh worker1 # or any other worker node
sudo systemctl stop ampq-consumer
```
to run consumer manually:
```
vagrant ssh worker1 # or any other worker node
sudo -u app -i
./consumer.py
```
# other

## queue
Queue name can be changed in Vagrantfile by adjusting ampq_queuename variable, default is:
```
ampq_queuename = 'hello'
```
after adjusting please run:
```
vagrant rsync && vagrant provision
```

## workers 
Workers can be added by icreasing node_count variable in Vagrantfile, default is:
```
node_count = 1
```
to bring up and provision new node after editing node count please run:
```
vagrant up && vagrant rsync && vagrant provision
```

## recreate
to recreate environmet from scratch:
```
 vagrant destroy -f && vagrant up
```
## destroy
remove environment:

```
 vagrant destroy -f
```

