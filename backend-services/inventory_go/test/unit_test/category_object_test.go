package unit

import (
	"github.com/stretchr/testify/assert"
	"inventory_go/category"
	"testing"
)

func TestRename_WithValidData_ShouldSucceed(t *testing.T) {
	originalName := "C1"
	newName := "C2"
	isNameUnique := true
	_category := category.NewCategory("I1", originalName, "")

	_, err := _category.Rename(newName, isNameUnique)

	assert.NoError(t, err)
}

func TestRename_WithNameNotUnique_ShouldReturnError(t *testing.T) {
	originalName := "C1"
	newName := "C2"
	isNameUnique := false
	_category := category.NewCategory("I1", originalName, "")

	_, err := _category.Rename(newName, isNameUnique)

	assert.Error(t, err)
}

func TestRename_WithEmptyName_ShouldReturnError(t *testing.T) {
	originalName := "C1"
	newName := ""
	isNameUnique := true
	_category := category.NewCategory("I1", originalName, "")

	_, err := _category.Rename(newName, isNameUnique)

	assert.Error(t, err)
}
