package rabbitmq

import (
	"fmt"
	"github.com/rabbitmq/amqp091-go"
	"log"
	"time"
)

func Connect(url string) (*amqp091.Connection, error) {
	var connection *amqp091.Connection
	var err error

	for i := 0; i < 5; i++ {
		connection, err = amqp091.Dial(url)
		if err == nil {
			return connection, nil
		}
		log.Printf("rabbitmq connect failed, retrying in 2s: %v", err)
		time.Sleep(2 * time.Second)
	}
	return nil, fmt.Errorf("could not connect to rabbitmq: %w", err)
}
