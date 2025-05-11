package transaction

import "inventory_go/infrastructure/models"

type TransactionRepository interface {
	InsertTransaction(transaction *Transaction) error
	GetByTransactionId(transactionId string) (*models.TransactionDocument, error)
	SetRolledBack(transactionId string) error
}
