sudo apt-get -qqy update
sudo apt-get -qqy install postgresql python-psycopg2
sudo apt-get -qqy install python-flask python-sqlalchemy
sudo apt-get -qqy install python-pip
pip install bleach
pip install oauth2client
pip install requests
pip install httplib2
su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb'
su vagrant -c 'createdb forum'
su vagrant -c 'psql forum -f /vagrant/forum/forum.sql'

vagrantTip="[35m[1mThe shared directory is located at /vagrant\nTo access your shared files: cd /vagrant(B[m"
echo -e $vagrantTip > /etc/motd

