FROM ubuntu:22.04
LABEL maintainer="kzhu28@my.bcit.ca"

# Install Python 3 and pip
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

# Install dependencies
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]