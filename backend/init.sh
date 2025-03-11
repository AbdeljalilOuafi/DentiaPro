sudo apt update
sudo apt install -y postgresql postgresql-contrib python3-pip python3-dev libpq-dev
pip3 install -r requirements.txt
# make a public domain/public shema
# make migrations for schemas and shared (public)