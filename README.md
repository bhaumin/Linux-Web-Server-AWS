P5: LINUX SERVER CONFIGURATION
==============================

Server
-------
IP Address: 52.27.252.176
Port: 2200


Application URL
----------------
http://ec2-52-27-252-176.us-west-2.compute.amazonaws.com/


Software Installed
-------------------

1. Finger

	```bash
	sudo apt-get install finger
	```

2. Apache

	```bash
	sudo apt-get install apache2
	```

3. python-setuptools, libapache2-mod-wsgi, python-flask, python-sqlalchemy, python-psycopg2, python-pip, oauth2client, dicttoxml

	```bash
	sudo apt-get install python-setuptools libapache2-mod-wsgi python-flask python-sqlalchemy python-psycopg2 python-pip oauth2client dicttoxml
	```

4. ntp

	```bash
	sudo apt-get install ntp
	```

5. git

	```bash
	sudo apt-get install git
	```

6. PostgreSQL

	```bash
	sudo apt-get install postgresql
	```

7. unattended-upgrades
	```bash
	sudo apt-get install unattended-upgrades
	sudo dpkg-reconfigure --priority=low unattended-upgrades
	```

8. fail2ban

	```bash
	sudo apt-get install fail2ban
	```

9. munin

	```bash
	sudo apt-get install munin
	```



Configuration Changes
----------------------

1. Upgraded the existing installed packages

	```bash
	sudo apt-get update
	sudo apt-get upgrade
	```

2. New user "grader" (password=ud@citygrad3r)

	```bash
	sudo adduser grader
	```
	
3. Made user grader a sudo user by creating the following file

	```bash
	sudo nano /etc/sudoers.d/grader
	```

4. Firewall rules as per the requirements

	```bash
	sudo ufw default deny incoming
	sudo ufw default allow outgoing
	sudo ufw allow 2200/tcp
	sudo ufw allow www
	sudo ufw allow ntp
	sudo ufw enable
	```

5. Changed the server timezone to UTC using the following utility

	```bash
	sudo dpkg-reconfigure tzdata
	```

6. Modified the following file

	```bash
	sudo nano /etc/ssh/sshd_config
	```
	
	```
	changed default ssh port to 2200
	Port 2200

	Change to no to disable tunnelled clear text passwords
	PasswordAuthentication no

	Disallow remote root login
	PermitRootLogin no
	```

7. New PostgreSQL database "catalog" and new database role named "catalog" (password=catal0g)

	```bash
	sudo -i -u postgres
	/etc/init.d/postgresql start &&\ psql --command "CREATE USER catalog WITH CREATEDB LOGIN PASSWORD 'catal0g';" &&\ createdb -O catalog catalog &&\ psql -U postgres -d catalog -c "REVOKE ALL ON SCHEMA public FROM public;" &&\ psql -U postgres -d catalog -c "GRANT ALL ON SCHEMA public TO catalog;"
	```

8. In order to be able to login as "grader", generate a ssh key locally and copy the corresponding public key on the server

	```bash
	echo 'run ssh-keygen on your machine'
	echo 'ssh-copy-id -p 2200 -i ~/.ssh/{your_pubkey_file} grader@52.27.252.176'
	echo 'ssh -p 2200 -i ~/.ssh/{your_privatekey_file} grader@52.27.252.176'

	```

9. Configure apache2 to setup and enable the virtual host for this catalogapp site
	- Copy catalogapp.conf to /etc/apache2/sites-available
	- Disabling the default site and enabling the catalogapp site with following commands

	```bash
	sudo a2ensite catalogapp
	sudo a2dissite 000-default
	sudo service apache2 reload
	```

10. [Configure](https://www.digitalocean.com/community/tutorials/how-to-install-munin-on-an-ubuntu-vps) the munin monitoring server

	Munin Monitor Server URL: http://52.27.252.176/munin/



udacity_key.rsa
----------------

```
MIIEowIBAAKCAQEAwiXjhfzBNjk76wR5ZLeSnLIbi21rZ8bdijZNynG3eVmqiUi4
OGEuRkXuIcPYl3p06jffw+okuWxL3LKy4J4J+Oinup7DRG8/JR6qBhV+wG2UDSJP
OnDt3XvQA4/MNsQQLbpMKShumlDswF2Ra4GdOPgz2tPqH2ZL7vfVZ2NAExdGJCiA
HbyPxZpYyf85akwc1+N8sYbNeTiRkOWUY7H0zyD+ej06WWs6Tb2+C2RrL2kvtdyA
luW/Lzyh2dvDaqVn5U0RAoraI2BvYdtQVFb48xWoDW9WQ1yz1sVt3nZK3rwdxDK8
jJq3vLoND/MgW2YUqJkGNBoJChNil6/z8FXHzQIDAQABAoIBAAnYF/hEP5u7PTGG
cY1MzY9KbKEeNDL332XRqRIZv/7UMBRz7ntVWh5QD2oA3yuXFvSFTsBFUAVi21ne
abl/6euICHEq+aWvqlj8fAyA7INfSwF7et7wuO7hB0QW93jTaiqXZqMznKAQeGCs
neIAmXM5CpAO7LEY48LDKDvsyWPuVIGaURm6ffU9dPVv3HN8oakHwboa2+sOV1vR
nsRBrIxXHEPdNTg6Q0tlyA23c/EgY7/tl+CsHE4a+o0NR2ZoE3t9S3HvwVXpWIml
1vZiGkPu6xCpDYJLOcLj7N0zqyfaKFdLFDxIByLLdCnQK3/arAm/1cLydUs67sht
yunp/EECgYEA8At7MJBn9fGkWKIieu6Z2C+Vwu+4RM7ZDi/gHONtwMeLq/rMXNUe
xu5UN1KvnwaNuOMJMgwenEZpQC84bEmoGRFNw6D/D4vOSN1R6PH5rk2xtsADWng7
FB6eroi3CiAgddyp3lbl7f1LDpxLo3pXeh4Fb0is2QxziJBYvRBrxNECgYEAzw1x
ZbxbBO69DbkEbX0Tokkg6GBOuYPBtKvnm5CQkFIu5BpoE5CCuQq9ni4TCtMWaIwA
FNHO/v4kws9mD0af8gehZaFlU/pb9SLmRAGZQT6bQa+22i2HxevyEl99byiqliaY
2fHkSfQ8nSGVDSvFgIv5FlvPKYsglSDL0yHKQj0CgYEAlmkLStXhXnmIWkVVx6PE
YHMIqzocQ3k9Bqe3DULwnZArk5q1/SFJhKsHuBamlsW7ffM86tAvSgrQnng4KZpJ
q1NtX7x8tdgLbRrI3Wbp5W8ngPR15XVax3OcSI6/6qdQz6lyAzB+KI7DPidvOcNK
FunCzAVE0Uf9CMAx6l3kuVECgYAqjLytB5Q840L+uvLp/TY3t4eHuaL0BNud4WXr
Vj4fKoRwY+zXeG8kz8w/4YAQTWjhe0PZA3Tieh/b2PtEUGM2PdMxK4XDSEP1kIJ5
n0p7Wf5V9WJCW/D2/5HzrKP+YAEOckgfIdKkUAjU0b3rwv8Hd7xsl9lu1CSSAPdi
ICOMkQKBgCkOcttdyM9LXEwYc5xJ8kXDeZE9WivRiTjtNyhZW/TGp/upgWuvcAYG
pzgmTF3NTK5vkTLUQlWJOvl4K2tZskqyOoqH5XrOon1XA+bXTLIGx8zgKa/SFxSb
zd18ng50VnMsIUp3h7p1QfqbBLUaF4RCEhBGUaUX6sim98VzzwVk
```
