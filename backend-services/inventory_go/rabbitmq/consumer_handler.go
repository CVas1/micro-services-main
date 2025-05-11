package rabbitmq

import (
	"encoding/json"
	"github.com/rabbitmq/amqp091-go"
	"inventory_go/product"
	"log"
)

type Envelope struct {
	Event         string          `json:"event"`
	Data          json.RawMessage `json:"data"`
	TransactionID string          `json:"transaction_id"`
}

type ReduceStockPayload struct {
	Products []struct {
		ProductID string `json:"product_id"`
		Quantity  int    `json:"quantity"`
	} `json:"products"`
}

type RollbackStockPayload struct {
	TransactionID string `json:"transaction_id"`
}

type ReduceResponse struct {
	Event         string      `json:"event"`
	Status        string      `json:"status"`
	Message       string      `json:"message"`
	Data          interface{} `json:"data"`
	TransactionId string      `json:"transaction_id"`
}

func HandleConsumer(consumer *Consumer, productService product.ProductService, publisher *Publisher) {
	err := consumer.Start(func(delivery amqp091.Delivery) {
		var env Envelope
		if err := json.Unmarshal(delivery.Body, &env); err != nil {
			log.Printf("rabbitmq: invalid envelope: %v", err)
			return
		}
		switch env.Event {
		case "reduce_stock":
			var payload ReduceStockPayload
			if err := json.Unmarshal(env.Data, &payload); err != nil {
				log.Printf("rabbitmq: bad reduce_stock payload: %v", err)
				return
			}
			transactionId := env.TransactionID
			for _, operation := range payload.Products {
				err := productService.ReduceStock(operation.ProductID, operation.Quantity, transactionId)
				if err != nil {
					response := &ReduceResponse{Event: "reduce_stock", Status: "error", Message: "", Data: nil, TransactionId: transactionId}
					bytes, err := json.Marshal(response)
					if err != nil {
						log.Printf("rabbitmq: failed to marshal response: %v", err)
						return
					}

					err = publisher.Publish(bytes)
					if err != nil {
						log.Printf("rabbitmq: failed to publish response: %v", err)
						return
					}
					return
				}
			}
			response := &ReduceResponse{Event: "reduce_stock", Status: "success", Message: "", Data: nil, TransactionId: transactionId}
			bytes, err := json.Marshal(response)
			if err != nil {
				log.Printf("rabbitmq: failed to marshal response: %v", err)
				return
			}
			err = publisher.Publish(bytes)
			if err != nil {
				log.Printf("rabbitmq: failed to publish response: %v", err)
				return
			}

		case "rollback_stock":
			var payload RollbackStockPayload
			if err := json.Unmarshal(env.Data, &payload); err != nil {
				log.Printf("rabbitmq: bad rollback_stock payload: %v", err)
				return
			}
			err := productService.StockRollback(payload.TransactionID)
			if err != nil {
				return
			}

		default:
			log.Printf("rabbitmq: unknown event %q", env.Event)
			err := delivery.Nack(false, false)
			if err != nil {
				return
			}
			return
		}

	})
	if err != nil {
		log.Fatal(err)
	}
}
