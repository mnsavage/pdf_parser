#type of container
FROM python:3.10

# working directory
WORKDIR /src

# install requirements
COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# get rest of folder in docker
COPY src/ ./


# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable for better Docker caching
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
# CMD directive is used as a default command which can be overridden when starting the container
CMD ["python", "./main.py"]