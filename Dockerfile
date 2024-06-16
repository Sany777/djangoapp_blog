# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN apt-get update \
    && apt-get install -y graphviz libgraphviz-dev pkg-config \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the project files into the container
COPY . .

# Command to run the graph models command
CMD ["python", "manage.py", "graph_models", "-a", "-o", "my_models.png"]
