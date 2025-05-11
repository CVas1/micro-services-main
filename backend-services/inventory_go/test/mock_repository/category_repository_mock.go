package mock_repository

import (
	"github.com/stretchr/testify/mock"
	"inventory_go/category"
	findmanyoptions "inventory_go/category/enums"
	"inventory_go/infrastructure/models"
)

type MockCategoryRepository struct {
	mock.Mock
}

func (r *MockCategoryRepository) GetById(id string) (*models.CategoryDocument, error) {
	args := r.Called(id)
	return args.Get(0).(*models.CategoryDocument), args.Error(1)
}
func (r *MockCategoryRepository) Save(category *category.Category) error {
	args := r.Called(category)
	return args.Error(0)
}

func (r *MockCategoryRepository) Delete(id string) error {
	args := r.Called(id)
	return args.Error(0)
}
func (r *MockCategoryRepository) FindByName(name string) (*models.CategoryDocument, error) {
	args := r.Called(name)
	return args.Get(0).(*models.CategoryDocument), args.Error(1)
}

func (r *MockCategoryRepository) FindManyByFilter(option findmanyoptions.FindManyOptions, id string) ([]*models.CategoryDocument, error) {
	args := r.Called(option, id)
	return args.Get(0).([]*models.CategoryDocument), args.Error(1)
}
