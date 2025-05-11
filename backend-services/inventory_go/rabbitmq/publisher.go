package rabbitmq

import (
	"github.com/rabbitmq/amqp091-go"
	"time"
)

type Publisher struct {
	channel   *amqp091.Channel
	queueName string
}

func NewPublisher(conn *amqp091.Connection, queueName string) (*Publisher, error) {
	ch, err := conn.Channel()
	if err != nil {
		return nil, err
	}

	_, err = ch.QueueDeclare(
		queueName,
		true,  // durable
		false, // auto-delete
		false, // exclusive
		false, // noWait
		nil,   // args
	)

	if err != nil {
		return nil, err
	}
	return &Publisher{channel: ch, queueName: queueName}, nil
}

func (p *Publisher) Publish(body []byte) error {
	return p.channel.Publish(
		"",          // empty exchange = default/direct
		p.queueName, // routing key = queue name
		false,       // mandatory
		false,       // immediate
		amqp091.Publishing{
			ContentType: "application/json",
			Body:        body,
			Timestamp:   time.Now(),
		},
	)
}
