# Python 3.11 slim — smallest official base
FROM python:3.11-slim

WORKDIR /main

# Install only essential system deps, then clean apt cache in the same layer
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first so this layer is cached on rebuilds
COPY requirements.txt .

# --no-cache-dir  → don't store the wheel cache
# --no-compile    → skip .pyc generation at install time
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# App code comes last — changes here won't bust the dep layer
COPY . .

ENV GOOGLE_API_KEY=""
ENV JWT_SECRET=""
ENV JWT_ALGORITHM="HS256"
ENV CLIENT_ID=""
ENV CLIENT_SECRET=""
ENV FRONTEND_URL="http://localhost:5173"
ENV DATABASE_URI=""

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]