package repositories

import "errors"

var (
	ErrCategoryNotFound = errors.New("category not found")
	ErrInvalidId        = errors.New("invalid id format")
	ErrMappingError     = errors.New("mapping error")
	ErrDuplicateKey     = errors.New("duplicate key error")
	ErrInvalidOption    = errors.New("invalid option")
	ErrProductNotFound  = errors.New("product not found")
)
