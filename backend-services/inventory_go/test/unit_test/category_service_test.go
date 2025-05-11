package unit

import (
	"github.com/stretchr/testify/assert"
	"go.mongodb.org/mongo-driver/v2/bson"
	"inventory_go/category"
	findmanyoptions "inventory_go/category/enums"
	"inventory_go/infrastructure/models"
	"inventory_go/infrastructure/repositories"
	"inventory_go/service"
	"inventory_go/test/mock_repository"
	"testing"
)

func TestCreateCategory_WithValidData_ShouldSucceed(t *testing.T) {
	categoryRepo := new(mock_repository.MockCategoryRepository)
	name := "C1"

	categoryRepo.On("FindByName", name).Return((*models.CategoryDocument)(nil), repositories.ErrCategoryNotFound)
	categoryRepo.On("Save", &category.Category{Id: "", Name: name, ParentId: ""}).Return(nil)

	categoryService := service.NewCategoryService(categoryRepo)
	err := categoryService.Create(&category.Category{Id: "", Name: name, ParentId: ""})

	assert.NoError(t, err)
	categoryRepo.AssertExpectations(t)
}

func TestCreateCategory_WithInvalidParentId_ShouldReturnError(t *testing.T) {
	categoryRepo := new(mock_repository.MockCategoryRepository)
	name := "C1"

	parentId := bson.NewObjectID()
	parentIdString := parentId.Hex()

	categoryRepo.On("GetById", parentIdString).Return((*models.CategoryDocument)(nil), nil)
	categoryRepo.On("FindByName", name).Return((*models.CategoryDocument)(nil), repositories.ErrCategoryNotFound)

	categoryService := service.NewCategoryService(categoryRepo)
	err := categoryService.Create(&category.Category{Id: "", Name: name, ParentId: parentIdString})

	assert.Error(t, err)
	categoryRepo.AssertExpectations(t)
}

func TestUpdateCategory_WithValidData_ShouldSucceed(t *testing.T) {
	categoryRepo := new(mock_repository.MockCategoryRepository)

	id := bson.NewObjectID()
	idString := id.Hex()
	originalName := "C1"
	newName := "C2"

	_category := &models.CategoryDocument{Id: id, Name: originalName, ParentId: bson.NilObjectID}

	categoryRepo.On("FindByName", newName).Return((*models.CategoryDocument)(nil), repositories.ErrCategoryNotFound)
	categoryRepo.On("GetById", idString).Return(_category, nil)
	categoryRepo.On("Save", category.NewCategory(idString, newName, "")).Return(nil)

	categoryService := service.NewCategoryService(categoryRepo)
	err := categoryService.Update(idString, newName)

	assert.NoError(t, err)
	categoryRepo.AssertExpectations(t)
}

func TestUpdateCategory_WithInvalidName_ShouldReturnError(t *testing.T) {
	categoryRepo := new(mock_repository.MockCategoryRepository)

	id := bson.NewObjectID()
	idString := id.Hex()
	originalName := "C1"
	newName := "C2"

	_category := &models.CategoryDocument{Id: id, Name: originalName, ParentId: bson.NilObjectID}

	categoryRepo.On("FindByName", newName).Return(_category, nil)

	categoryService := service.NewCategoryService(categoryRepo)
	err := categoryService.Update(idString, newName)

	assert.Error(t, err)
	categoryRepo.AssertExpectations(t)
}

func TestDeleteCategory_WithValidData_ShouldSucceed(t *testing.T) {
	categoryRepo := new(mock_repository.MockCategoryRepository)

	id := bson.NewObjectID()
	idString := id.Hex()
	var emptyCategoryArray []*models.CategoryDocument

	categoryRepo.On("Delete", idString).Return(nil)
	categoryRepo.On("FindManyByFilter", findmanyoptions.FindAllSubCategoriesById, idString).Return(emptyCategoryArray, nil)

	categoryService := service.NewCategoryService(categoryRepo)
	err := categoryService.Delete(idString)

	assert.NoError(t, err)
	categoryRepo.AssertExpectations(t)
}

func TestDeleteCategory_WithSubcategoriesStillExist_ShouldReturnError(t *testing.T) {
	categoryRepo := new(mock_repository.MockCategoryRepository)

	id := bson.NewObjectID()
	idString := id.Hex()
	populatedCategoryArray := []*models.CategoryDocument{&models.CategoryDocument{Id: bson.NewObjectID(), Name: "C1", ParentId: id}}

	categoryRepo.On("FindManyByFilter", findmanyoptions.FindAllSubCategoriesById, idString).Return(populatedCategoryArray, nil)

	categoryService := service.NewCategoryService(categoryRepo)
	err := categoryService.Delete(idString)

	assert.Error(t, err)
	categoryRepo.AssertExpectations(t)
}
