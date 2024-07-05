# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install setuptools wcwidth wheel mysql-connector-python keyboard prettytable


# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run app.py when the container launches
CMD python3 ./mail_check.py