FROM python:3.13-alpine AS builder

WORKDIR /app

# alpine specific build tools
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev postgresql-dev

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --user -r requirements.txt

COPY . .

FROM python:3.13-alpine
WORKDIR /app
# Install only runtime dependencies
RUN apk add --no-cache libffi openssl postgresql-libs
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8080