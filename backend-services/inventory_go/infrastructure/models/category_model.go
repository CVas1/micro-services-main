package models

import "go.mongodb.org/mongo-driver/v2/bson"

type CategoryDocument struct {
	Id       bson.ObjectID `bson:"_id"`
	Name     string        `bson:"name"`
	ParentId bson.ObjectID `bson:"parent_id"`
}
