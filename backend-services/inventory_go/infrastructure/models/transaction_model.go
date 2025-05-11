package models

import "go.mongodb.org/mongo-driver/v2/bson"

type TransactionDocument struct {
	Id            bson.ObjectID `bson:"_id"`
	TransactionId string        `bson:"transaction_id"`
	ProductId     string        `bson:"product_id"`
	Stock         int           `bson:"stock"`
	RolledBack    bool          `bson:"rolled_back"`
}
