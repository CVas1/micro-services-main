package mock_repository

import (
	"github.com/stretchr/testify/mock"
	"inventory_go/infrastructure/models"
	"inventory_go/product"
	findmanyproductoptions "inventory_go/product/enums"
)

type MockProductRepository struct {
	mock.Mock
}

func (r *MockProductRepository) GetById(id string) (*models.ProductDocument, error) {
	args := r.Called(id)
	return args.Get(0).(*models.ProductDocument), args.Error(1)
}

func (r *MockProductRepository) Save(product *product.Product) error {
	args := r.Called(product)
	return args.Error(0)
}

func (r *MockProductRepository) Delete(id string) error {
	args := r.Called(id)
	return args.Error(0)
}

func (r *MockProductRepository) GetStock(id string) (int, error) {
	args := r.Called(id)
	return args.Int(0), args.Error(1)
}

func (r *MockProductRepository) FindManyByFilter(
	option findmanyproductoptions.FindManyProductOptions,
	name string,
	categoryId string,
) ([]*models.ProductDocument, error) {
	args := r.Called(option, name, categoryId)
	return args.Get(0).([]*models.ProductDocument), args.Error(1)
}
