FROM python:3.11-slim

WORKDIR /app

#install requirements

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . /app/
EXPOSE 5003

# Set the entrypoint for the container
CMD ["hypercorn", "--bind", "0.0.0.0:5003", "app.__init__:app"]
