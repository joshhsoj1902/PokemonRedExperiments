FROM python:3.10-bookworm

# Set the working directory in docker
WORKDIR /pokemon

# Install system dependencies
RUN apt-get update && apt-get install -y \
  build-essential \
  git && \
  # Clean up apt cache to reduce image size.
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
  ffmpeg && \
  # Clean up apt cache to reduce image size.
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

RUN mkdir baselines

COPY baselines/requirements.txt baselines

# Install Python dependencies
RUN pip install --no-cache-dir -r baselines/requirements.txt

RUN pip install websockets

# Copy source-code
# COPY . .

WORKDIR /pokemon/baselines

# Command to run at container start
CMD [ "python", "run_baseline_parallel_fast.py" ]
