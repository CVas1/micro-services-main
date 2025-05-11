package mock_repository

import (
	"github.com/stretchr/testify/mock"
	"inventory_go/infrastructure/models"
	"inventory_go/transaction"
)

type MockTransactionRepository struct {
	mock.Mock
}

func (r *MockTransactionRepository) InsertTransaction(transaction *transaction.Transaction) error {
	args := r.Called(transaction)
	return args.Error(0)
}

func (r *MockTransactionRepository) GetByTransactionId(transactionId string) (*models.TransactionDocument, error) {
	args := r.Called(transactionId)
	return args.Get(0).(*models.TransactionDocument), args.Error(1)
}

func (r *MockTransactionRepository) SetRolledBack(transactionId string) error {
	args := r.Called(transactionId)
	return args.Error(0)
}
