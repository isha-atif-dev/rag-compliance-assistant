FROM python:3.11-slim

WORKDIR /app

# Install the CPU-only build of torch FIRST, explicitly, before the main
# requirements install. The default PyPI torch wheel bundles full NVIDIA
# CUDA/GPU libraries (several GB) even on servers with no GPU at all,
# like this one. The CPU-only build skips all of that.
RUN pip install --no-cache-dir torch==2.14.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]