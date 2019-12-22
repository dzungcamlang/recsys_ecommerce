```
RecSys_ecommerce
|
|-recsys
|
|-site_src
```

# Local users

### Setup

`python -m pip install -r requirements.txt`

or

`python3 -m pip install -r requirements.txt`

### Run web server

`python site_src/manage.py runserver`

### Run Recsys api

`python recsys/api.py`

# Docker users

`docker build . -t iuthesis_recsys_web:latest`

`docker-compose up`