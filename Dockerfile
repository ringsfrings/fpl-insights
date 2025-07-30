# Use a slim Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY fpl/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and templates
COPY fpl/fpl_app.py ./fpl_app.py
COPY fpl/templates ./templates

# Expose the port the Flask app listens on
EXPOSE 5000

# Run the Flask app
CMD ["python", "fpl_app.py"]
