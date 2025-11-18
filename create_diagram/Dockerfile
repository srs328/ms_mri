# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy your script and any static files into the container
COPY create_diagram.py ./
COPY template_diagram.png ./
COPY color_reference.csv ./
COPY structure_reference.csv ./

# Install required Python packages
RUN pip install --no-cache-dir numpy pandas pillow

# Set default command to run the script
ENTRYPOINT ["python", "create_diagram.py"]