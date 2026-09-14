# Start from a small, official Python image, already has Python installed,
# nothing else. "slim" means minimal extras, keeps the final image smaller.
FROM python:3.11-slim

# All following commands run from this folder inside the container
WORKDIR /app

# Copy just the requirements file first (not all your code yet), install
# dependencies, this ordering matters: Docker caches each step, so if your
# code changes but requirements.txt doesn't, this slow install step gets
# skipped on the next rebuild instead of rerunning every time
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your actual project code into the container
COPY . .

# Documents which port this container listens on (informational, doesn't
# actually open the port by itself, that happens when we run it)
EXPOSE 8000

# The command that runs when the container starts.
# --host 0.0.0.0 is essential here: 127.0.0.1 would only be reachable
# from inside the container itself, 0.0.0.0 means "listen on every
# network interface," which is what lets anything outside the container
# (your browser, another container) actually reach it
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]