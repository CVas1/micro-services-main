package rabbitmq

import (
	"github.com/rabbitmq/amqp091-go"
	"log"
)

type Consumer struct {
	channel   *amqp091.Channel
	queueName string
}

func NewConsumer(conn *amqp091.Connection, queueName string) (*Consumer, error) {
	ch, err := conn.Channel()
	if err != nil {
		return nil, err
	}

	_, err = ch.QueueDeclare(
		queueName, // name
		true,      // durable
		false,     // autoDelete
		false,     // exclusive
		false,     // noWait
		nil,       // args
	)
	if err != nil {
		return nil, err
	}
	return &Consumer{channel: ch, queueName: queueName}, nil
}

func (c *Consumer) Start(onMessage func(amqp091.Delivery)) error {
	msgs, err := c.channel.Consume(
		c.queueName,
		"",    // consumer tag
		false, // autoAck
		false, // exclusive
		false, // noLocal
		false, // noWait
		nil,   // args
	)
	if err != nil {
		return err
	}

	go func() {
		for d := range msgs {
			onMessage(d)
			if err := d.Ack(false); err != nil {
				log.Printf("rabbitmq: failed to ack message: %v", err)
			}
		}
	}()

	return nil
}
