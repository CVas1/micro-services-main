package service

import "errors"

var (
	ErrIdShouldBeEmpty                     = errors.New("id should be empty when creating")
	ErrDuplicateCategoryName               = errors.New("duplicate category name")
	ErrInvalidParentCategory               = errors.New("invalid parent category")
	ErrInvalidCategoryName                 = errors.New("invalid category name")
	ErrCantDeleteCategoryWithSubcategories = errors.New("can't delete category with subcategories")

	ErrCategoryTreeIsEmpty = errors.New("category tree is empty")

	ErrProductValidationFailed = errors.New("product validation failed")
)
