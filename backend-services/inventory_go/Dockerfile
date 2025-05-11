# Start from the official Go image as the build stage
ARG GO_VERSION=1.24
FROM golang:${GO_VERSION}-bullseye AS builder

# Set the Current Working Directory inside the container
WORKDIR /app

# Copy go mod and sum files
COPY go.mod ./

# Download all dependencies
RUN go mod download

# Copy the source code
COPY . .

# Build the Go app
RUN go build -o main .

# Now use a smaller image to run the binary
FROM debian:bullseye-slim

# Set the working directory inside the runtime container
WORKDIR /app

# Copy the binary from the builder image
COPY --from=builder /app/main .

# Copy swagger docs
COPY --from=builder /app/docs ./docs

# Expose port (optional, just for documentation)
EXPOSE 9292

# Command to run the executable
CMD ["./main"]