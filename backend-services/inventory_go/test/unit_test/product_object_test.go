package unit

import (
	"github.com/stretchr/testify/assert"
	"inventory_go/product"
	"testing"
)

func TestRenameProduct_WithValidData_ShouldSucceed(t *testing.T) {
	originalName := "P1"
	newName := "P2"
	_product := product.NewProduct("I1", originalName, 15.5, 100, "V1", "Image", "C1", "some description")

	err := _product.Rename(newName)

	assert.NoError(t, err)
}

func TestRenameProduct_WithSameName_ShouldReturnError(t *testing.T) {
	originalName := "P1"
	newName := "P1"
	_product := product.NewProduct("I1", originalName, 15.5, 100, "V1", "Image", "C1", "some description")

	err := _product.Rename(newName)

	assert.Error(t, err)
}

func TestRenameProduct_WithEmptyName_ShouldReturnError(t *testing.T) {
	originalName := "P1"
	newName := ""
	_product := product.NewProduct("I1", originalName, 15.5, 100, "V1", "Image", "C1", "some description")

	err := _product.Rename(newName)

	assert.Error(t, err)
}

func TestRepriceProduct_WithValidData_ShouldSucceed(t *testing.T) {
	originalPrice := 15.5
	newPrice := 16.5
	_product := product.NewProduct("I1", "P1", originalPrice, 100, "V1", "Image", "C1", "some description")

	err := _product.Reprice(newPrice)

	assert.NoError(t, err)
}

func TestRepriceProduct_WithNegativePrice_ShouldReturnError(t *testing.T) {
	originalPrice := 15.5
	newPrice := -16.5
	_product := product.NewProduct("I1", "P1", originalPrice, 100, "V1", "Image", "C1", "some description")

	err := _product.Reprice(newPrice)

	assert.Error(t, err)
}

func TestRedescribeProduct_WithValidData_ShouldSucceed(t *testing.T) {
	originalDescription := "some description"
	newDescription := "new description"
	_product := product.NewProduct("I1", "P1", 15.5, 100, "V1", "Image", "C1", originalDescription)

	err := _product.Redescribe(newDescription)

	assert.NoError(t, err)
}

func TestRedescribeProduct_WithEmptyDescription_ShouldReturnError(t *testing.T) {
	originalDescription := "some description"
	newDescription := ""
	_product := product.NewProduct("I1", "P1", 15.5, 100, "V1", "Image", "C1", originalDescription)

	err := _product.Redescribe(newDescription)

	assert.Error(t, err)
}
