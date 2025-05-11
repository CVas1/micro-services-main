package infrastructure

import (
	"context"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
	"log"
	"os"
	"time"
)

func Connect() (*mongo.Client, error) {
	uri := os.Getenv("MONGO_URL")
	if uri == "" {
		uri = "mongodb://localhost:27017"
	}

	clientOptions := options.Client().ApplyURI(uri)

	client, err := mongo.Connect(clientOptions)

	if err != nil {
		log.Fatalf("mongo.Connect error: %v", err)
		return nil, err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := client.Ping(ctx, nil); err != nil {
		log.Fatalf("mongo.Ping error: %v", err)
		return nil, err
	}

	log.Println("✅ Connected to MongoDB")
	return client, err
}
