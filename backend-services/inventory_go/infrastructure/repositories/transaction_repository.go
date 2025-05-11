package repositories

import (
	"context"
	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
	"inventory_go/infrastructure/models"
	"inventory_go/transaction"
	"inventory_go/transaction/mappers"
	"time"
)

type TransactionRepositoryImpl struct {
	collection *mongo.Collection
}

func NewTransactionRepository(db *mongo.Database, collectionName string) *TransactionRepositoryImpl {
	return &TransactionRepositoryImpl{
		collection: db.Collection(collectionName),
	}
}

func (r *TransactionRepositoryImpl) InsertTransaction(transaction *transaction.Transaction) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	document := mappers.MapTransactionToModel(transaction)
	id := bson.NewObjectID()
	document.Id = id
	_, err := r.collection.InsertOne(ctx, document)
	return err
}

func (r *TransactionRepositoryImpl) GetByTransactionId(transactionId string) (*models.TransactionDocument, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	filter := bson.M{"transaction_id": transactionId}
	var document models.TransactionDocument
	err := r.collection.FindOne(ctx, filter).Decode(&document)
	return &document, err
}

func (r *TransactionRepositoryImpl) SetRolledBack(transactionId string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	document, err := r.GetByTransactionId(transactionId)
	if err != nil {
		return err
	}

	document.RolledBack = true
	filter := bson.M{"transaction_id": transactionId}
	update := bson.M{"$set": document}
	_, err = r.collection.UpdateOne(ctx, filter, update, options.UpdateOne().SetUpsert(false))
	return err
}
