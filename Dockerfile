FROM bitnami/spark

# Copy the Python script into the Docker image
COPY github_streaming_app.py /app/github_streaming_app.py

# Set the working directory
WORKDIR /app

# Run the script
CMD ["spark-submit", "github_streaming_app.py"]
