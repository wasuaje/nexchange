This file describes the wercker pipelines in this project and documents the configuration vars. All the pipelines are using the same image, which is `pitervergara/geodjango:nexchange`. This image is based on python:3.5 and adds geodjango required libs plus the python packages required by nexchange project at the time of the image creation. You can see the image details at https://hub.docker.com/r/pitervergara/geodjango/

# Dev #
run `$ wercker dev --publish 8000` to start container
On dev pipeline, a docker container based on the public image is started and the app directory is mounted inside the container. The DJANGO_SETTINGS_MODULE is setted to **'nexchange.settings_dev'** and the variables from **ENVIRONMENT** file are exported by wercker. Then, the python requirements and the bower dependencies are installed, the migrations are created and applied. After all these steps, the django runserver command is executed, starting the server on port 8000.

# Build #
run `$ wercker build` to check if the build will go OK when you push your code

Build pipelines looks like the 'dev' one. But after starting the container DJANGO_SETTINGS_MODULE is setted to **'nexchange.settings_prod'**. If the build is local the variables from  **ENVIRONMENT** file are exported, if the build is remote the variables defined in the web interface of wercker are exported.

During this pipeline, besides the steps executed in dev pipeline, the Django management commands **collectstatic** is also executed.

Close to the end, the *echo python information* step prints a few useful data about python and python package versions in this build

The step (_copy files_) copies data into the contianer, to the places they should be for runnning on production. The static and media, will be later copied again to another place. This is done in a second step because the container should be already in execution and with the volumes mounted (which is not the case during the build).

The build pipeline also creates an entripoint script at **/entrypoint.sh**, inside the container. This is the script executed by the container as soon as it starts.

Once all the files are in place, the **internal/docker-push** step publishes the image in docker hub. It sends the image to the $DOCKER_HUB_REPO repo, tagging it according to the **DOCKER_IAMGE_TAG** environment variable.


# Tests #
The test pipeline builds the container run tests and exit. 

After starting the container DJANGO_SETTINGS_MODULE is setted to **'nexchange.settings_test'**. If the build is local the variables from  **ENVIRONMENT** file are exported, if the build is remote the variables defined in the web interface of wercker are exported.

The pipeline installs all the requirements (frontend and backend), creates and runs migrations and loads the fixtures. After that, the backend test as triggered with `django manage.py run test`. The next step runs frontend tests with `npm run-script test` which will invoke the corresponding script inside the file **package.json**.
The tests are runned by [karma](https://karma-runner.github.io/0.13/index.html), using the headless *browser* [phantomjs](http://phantomjs.org/).

Karma is configured via **karma.conf** file and **it's important that 3rd libs** including those installed via bower are added  to the section *files* in this configuration. 

The test files that will be running are the ones into **static/js/tests/spec** directory, they shoul be written using the [jasmine](http://jasmine.github.io/2.4/introduction.html). Fixture .html files placed into **static/js/tests/fixtures/** will be served by karma and can be loaded in your test spec with the [jasmine-jquery](https://github.com/velesin/jasmine-jquery) extension.

**If the tests are tiggered via the pre-commit hook script**, the script will look for a running instance of the nexchange container (supposedly started with wercker dev). If it finds one, it will try to run the tests inside this instance to minimize the time spent on the job. If no container is found, then one is created as described above int this section.
The container will be searched via docker ps with these filters:
`docker ps -q --filter "ancestor=pitervergara/geodjango:nexchange" --filter name="wercker-pipeline-" --filter status=running`


# Deploy #
In this step the pipeline remotely login into the target server ($DEST_HOST_ADDR) and uses docker-compose to pull the last version of the image (according to the TAG) and then restarts the containers, also using docker-compose.

## At wercker web servers ##
Besides creating the image, at this point the pipeline copies the **docker-compose.yml** and the **nginx.conf** file to the destination server (they go into the folder **/nexchange**).
After coping the files via scp, the pipeline SSH into the server and runs a series of commands.

## At the target server ##
The *Do deploy* step connects to *$SSH_USER@$DEST_HOST_ADDR* and executes the steps to pull and restart the containers.

After connecting on the remote server, the step logs in to dockerub (so the repo might be a private one) and pulls the images with `docker-compose pull` which will download the latest version of the ${DOCKER_HUB_REPO}:${DOCKER_IMAGE_TAG}  image, which was pushed in the build pipeline.
This same command will also pull the newest versions of the image for the nginx container and for the postgres container.
Once the images are there, `docker-compose restart` is invoked to restart the containers based on these new images.

The connections between the containers are handled by docker-compose, according to the definitions at the docker-compose.yml file.

## In the target server, at run time (the entrypoint script) ##
When the app (Django) container starts, the entrypoint script exports a few variables, and enters in a loop, waiting for the connection to the postgis server to be ready. 

When postgres is accepting connections, the entrypoin runs the **migrate** management command to apply in the production database the new migrations created at build time (if any). 
Then, the script copies the static and media files to the **/usr/share/nginx/html** which is expected to be a volume from the host, which is also mounted inside the nginx container. 
This mounts are also handled by docker-compose and described in the docker-compose.yml file.

The script also try to create a django usper user and starts a backgroud process to monitor the gunicorn logs (which allows `docker logs container` to show gunicorn logs).

After all this, the script start the gunicorn server at 0.0.0.0:${GUNICORN_PORT}. This is done via a call to `newrelic-admin run-program` which takes care of invoking Gunicorn and **send statistics reports to New Relic**.


### About the database ###
For dev and build pipelines a service with postgres+postgis is used. The life cycle and linking of this service container is totally managed by wercker.

At the deploy targets the database is managed by docker-compose. The user, password and database name are all defined in wercker web inteface and exported by the deploy script (*do-deploy* step) in the target host just before calling docker-compose, which in turns gets these variables from the env.

The related variables (which the values you can check at wercker web) are: 
- POSTGIS_ENV_POSTGRES_USER
- POSTGIS_ENV_POSTGRES_PASSWORD
- POSTGIS_ENV_POSTGRES_DB

They are also printed on the **do deploy** step, so you can check the logs at wercker web to see these values.

Currently, the database container is running an instance of [mdillon/postgis](https://hub.docker.com/r/mdillon/postgis/) image (the same one used in dev and build steps). 
The data is saved on the host at the */nexchange/database* directory (docker automatically creates it when the container starts for the first time).


### About the Web Server ###
For dev pipeline there is no webserver other than Django ( *python manage.py runserver* ), which is called via `newrelic-admin run-program` allowing developer to have **New Relic** statistics at dev (the NEW_RELIC_LICENSE_KEY used here is defined in the ENVIRONMENT FILE).

At deploy targets, a **Ngix** container acts as a reverse proxy to gunicorn. The cofiguration file used inside the container is **nginx.conf**. The same file is currently used in all deploy targets. 

For the SSL, in production we have **Certificates signed by Comodo**. The other target servers use certificates providade by the **Let's encrypt CA**.
In any case, the certificates files are placed in the host at **/nexchange/ssl** and mounted inside the container.

The image for the Nginx cames from the repository **onitsoft/nginx** and we always use the *latest* tag.

The container is instantiated by docker-compose and the linking between it and the app (Django/Gunicorn) container is handled by compose to.

----
# Enviroment variables #
## for dev ##

## for build and deploy ##
- `PEM_FILE_CONTENT` - The key to SSH into server (create key par via wercker web interface. remeber to install public key on target server)
- `SSH_USER` - the user to SSH into server
- `DEST_HOST_ADDR` - server where to deploy 
- `DATABASE_CONTAINER` - DB container to which the container will be linked
- `POSTGIS_ENV_POSTGRES_USER` - DB username used to connect to DATABASE_CONTAINER
- `POSTGIS_ENV_POSTGRES_PASSWORD` - the password for POSTGIS_ENV_POSTGRES_USER
- `POSTGIS_ENV_POSTGRES_DB` - the name of the database to connect to
- `GUNICORN_PORT` - the port in which gunicorn will run inside the container 
- `VOLUMES_PARAM` - a list o volumes (each preceded by -v to mount in container)
- `PORTS_PARAM` - a list of ports (preceded by -p) to expose from the container 
- `DOCKER_HUB_USER` - dockerhub username to push and pull container images
- `DOCKER_HUB_PASSWORD` - password for DOCKER_HUB_USER (define it as a protectd var)
- `DOCKER_HUB_REPO` - the dockerhub repo where to push (repo must already exists and could be  private)
- `NEW_RELIC_CONFIG_FILE` - The name of the file inside the project which contains the New Relic Python angent configuration
- `NEW_RELIC_ENVIRONMENT` - The name of the environment. New Relic agent takes it into account to specialize config
- `NEW_RELIC_LICENSE_KEY` - The key of the New Relic account to which the data should be sent
- `DOCKER_IMAGE_TAG` - The TAG that will be apllied to the image produced by this build pipeline
- `DJANGO_SETTINGS_MODULE`- The Django module configuration that should be used in this pipeline



----
# Other useful informations

# The **ticker** component ????? #

## How to configure a new server as a deployment target 

### Pipeline and Workflow in wercker web 
Start by creating a pipeline for build and another for deploy to your new target
This is done via wercker web interface. Ensure that you have these variables defined:
- For build pipeline
-- DJANGO_SETTINGS_MODULE
-- NEW_RELIC_ENVIRONMENT
-- DOCKER_IMAGE_TAG 

- For deploy pipeline
-- DEST_HOST_ADDR
-- DOCKER_IMAGE_TAG
-- PEM_FILE_CONTENT

(For details about each of these variables, check the *Enviroment variables* section of this file)

After you create the pipelines, you can add them to the workflow, via wercker web.


### Configure the server ###
Considering a fresh new instance of Ubuntu 16 at Digital Ocean

- Update the SO
```
# apt-get update
# apt-get upgrade -y
```

- Install docker on the server
You can find details on [this page](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04)

```
# apt-get update
# apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
# echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee /etc/apt/sources.list.d/docker.list
# apt-get update
# apt-cache policy docker-engine
# apt-get install -y docker-engine
```

- Install docker-compose on the server
You can find details on [this page](https://docs.docker.com/compose/install/)
```
# curl -L https://github.com/docker/compose/releases/download/1.7.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose`
# chmod +x /usr/local/bin/docker-compose`
```

- Create a user to be used by the wercker web interface
```
# useradd -u 1000 -s /bin/bash --comment "Deployment User" -d /home/wercker wercker
```
- Create and install the public key which the deploy script will use to SSH into the server. (This is the key that you create in the *Pipeline and Workflow in wercker web* stage above):
```
# mkdir -p /home/wercker/.ssh
# echo "PUT SSH PUBLIC KEY HERE. THIS APPEARS IN WERCKER INTERFACE AS *PEM_FILE_CONTENT_PUBLIC*" > /home/wercker/.ssh/authorized_keys 
# chmod 700 /home/wercker/.ssh
# chmod 600 /home/wercker/.ssh/authorized_keys
# chown -R wercker:wercker /home/wercker
```

- Allow the deploy user to run docker and docker-compose with sudo, preserving the environment and without asking for password
```
# echo "wercker ALL=(ALL) NOPASSWD:SETENV: /usr/bin/docker, /usr/local/bin/docker-compose" > /etc/sudoers.d/wercker
```

- Run the nginx container once, for creating the SSL certificate and key
```
# mkdir -p /nexchange/letsencypt
# docker run --rm -it -p 80:80 -p 443:443 -v /nexchange/letsencypt/:/etc/letsencrypt onitsoft/nginx /bin/bash
## inside the container run 
# certbot certonly --standalone --non-interactive --agree-tos --email webmaster@nexchange.ru -d <THE FQDN OF YOUR TARGET>
## CTRL + D to exit container
```

- Create symbolic links to the letsencrypt certificates in the place that nginx expect to find the certs:
```
# mkdir -p /nexchange/etc/nginx/ssl/
# cd /nexchange/etc/nginx/ssl/
# ln -s /etc/letsencrypt/live/staging.nexchange.ru/fullchain.pem fullchain.pem
# ln -s /etc/letsencrypt/live/staging.nexchange.ru/privkey.pem privkey.pem
## These synlink will look broken on the host, but they will work once mounted inside the container (docker-compose takes care of the mounting)
```
- Ensure that the deploy user can write on directory, during deploy
```
# chown wercker:wercker /nexchange
# chown -R wercker:wercker /nexchange/etc/nginx
```
