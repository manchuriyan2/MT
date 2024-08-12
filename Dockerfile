FROM python:3.11

RUN apt update -y && apt upgrade -y && \
    apt install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copy the repository files into the container
COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

# Ensure the start script is executable
RUN chmod +x start

# Use the start file as the entrypoint
CMD ["bash", "start"]
