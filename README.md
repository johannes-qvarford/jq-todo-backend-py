# jq-todo-backend-py

Used package repositories on Ubuntu:

> sudo add-apt-repository ppa:deadsnakes/ppa

Used packages on Ubuntu:

> sudo apt install python3.10 python3.10-distutils python3.10-dev build-essential

Installed poetry using:

> curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

Installed the Python extension using the following vsc command:

> ext install ms-python.python

Initialize project using:

> poetry install

Check the install-pre-commit file for how to run formatting, static type checking and testing.

Run the following to build and run the application in docker.

> docker build -t jq-todo-backend .

> docker run -d --name jq-todo-backend -p 8080:8080 jq-todo-backend

If you are running the app in WSL and want to access it from Windows, start it on the ip address for the ethernet device (eth0.inet from `ifconfig` command). You can use the same ip address+port when accessing from Windows.

> poetry run uvicorn jqtodobackend.backend:app --host 172.23.59.68 --port 8080

Follow [this article](https://marcobelo.medium.com/setting-up-python-black-on-visual-studio-code-5318eba4cd00) on how to install formatting on save in vsc using black.