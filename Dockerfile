FROM ubuntu/postgres:14-22.04_edge

# Set working directory
WORKDIR /lot_sizing

# Update infrastructure for CBC solver and all Python modules listed in requirements.txt
RUN apt-get update -y
RUN apt-get install -y build-essential \
    git \
    bash \
    gfortran \
    coinor-cbc \
    libpq-dev \
    coinor-libcbc-dev \
    python3-psycopg2 \
    python3.11 \
    python3-pip

# Setup Python runtime
ADD requirements.txt requirements.txt
RUN pip install --prefer-binary --no-cache-dir --upgrade -r requirements.txt

# Copy SQL files for creation of persistent tables and virtual views (EER model)
COPY init.sql /docker-entrypoint-initdb.d/

# Copy python projects (including experiments)
COPY numerical_experiments .