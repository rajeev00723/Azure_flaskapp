FROM python:3.9-slim-buster
# Packages required to run the Azure CLI installation
RUN	apt-get update && apt-get -y install curl

# Azure installation command
RUN	curl -sL https://aka.ms/InstallAzureCLIDeb | bash

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt -i https://artifactory.dhl.com/artifactory/api/pypi/pypi/simple
COPY . .
EXPOSE 5000
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host", "0.0.0.0"]