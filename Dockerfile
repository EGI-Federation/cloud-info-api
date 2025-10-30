FROM python:3.13-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Add Tini
# See https://github.com/krallin/tini
# This avoids the healthcheck becoming zombie processes
ENV TINI_VERSION=v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

RUN adduser python
USER python

# Install httpie for the healthcheck
RUN uv tool install httpie

# Copy the application into the container.
COPY --chown=python . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

EXPOSE 80/tcp

HEALTHCHECK CMD uv tool run --from httpie http localhost

# Run the application.
ENTRYPOINT ["/tini", "--"]
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]
