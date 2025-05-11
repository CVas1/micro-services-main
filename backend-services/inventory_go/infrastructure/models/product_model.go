package models

import "go.mongodb.org/mongo-driver/v2/bson"

type ProductDocument struct {
	Id          bson.ObjectID `bson:"_id"`
	Name        string        `bson:"name"`
	Price       float64       `bson:"price"`
	Stock       int           `bson:"stock"`
	VendorId    string        `bson:"vendor_id"`
	Image       string        `bson:"image"`
	Description string        `bson:"description"`
	CategoryId  bson.ObjectID `bson:"category_id"`
}
