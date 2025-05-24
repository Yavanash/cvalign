# --- Build stage ---
FROM golang:1.24 AS builder

WORKDIR /app

# Cache dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source and build
COPY . .
RUN go build -o /bin/main ./cmd

# --- Runtime stage ---
FROM golang:1.24

WORKDIR /app

COPY --from=builder /bin/main .
COPY .env .env

EXPOSE 8080

CMD ["./main"]