genewiki
========

The GeneWiki Project

### Setup
ssh -i ~/.ssh/genewiki_webserver.pem.txt ubuntu@34.201.165.246  

$ virtualenv -p /usr/bin/python3 genewiki_venv

$ source genewiki_venv/bin/activate

$ git clone https://github.com/SuLab/GeneWikiCentral.git

$ scp GeneWikiCentral/genewiki/genewiki/settings.py ubuntu@34.201.165.246:/home/ubuntu/GeneWikiCentral/genewiki/genewiki
settings.py 
 
$ sudo apt-get install libmysqlclient-dev

$ sudo apt-get install libncurses5-dev

$ cd GeneWikiCentral/genewiki/

$ pip install -r requirements.txt

python import os os.environ['DJANGO_SETTINGS_MODULE'] = 'genewiki.settings'

add genewiki/settings.py allowed_hosts =['34.201.165.246'...

$python manage.py migrate

$python manage.py collectstatic

$ sudo ln -s /home/ubuntu/GeneWikiCentral/genewiki/genewiki_nginx.conf /etc/nginx/sites-enabled/genewiki_nginx.conf

$ sudo /etc/init.d/nginx start

from GeneWikiCentral/genewiki run

$ uwsgi --socket :8001 --module genewiki.wsgi

If IP changes you need to:

1. added to allowed hosts in the settings.py file

2. add IP to server_name in the genewiki_nginx.conf file

3. restart wsgi and restart nginx

sudo /etc/init.d/nginx restart

sudo fuser -k 8001/tcp

uwsgi --socket :8001 --module genewiki.wsgi


