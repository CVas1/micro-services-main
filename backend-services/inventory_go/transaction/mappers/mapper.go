package mappers

import (
	"go.mongodb.org/mongo-driver/v2/bson"
	"inventory_go/infrastructure/models"
	"inventory_go/transaction"
)

func MapTransactionToModel(transaction *transaction.Transaction) *models.TransactionDocument {
	return &models.TransactionDocument{
		TransactionId: transaction.TransactionId,
		ProductId:     transaction.ProductId,
		Stock:         transaction.Stock,
		RolledBack:    false,
		Id:            bson.NilObjectID,
	}
}
