package category

import (
	findmanyoptions "inventory_go/category/enums"
	"inventory_go/infrastructure/models"
)

type CategoryRepository interface {
	GetById(id string) (*models.CategoryDocument, error)
	Save(category *Category) error
	Delete(id string) error
	FindByName(name string) (*models.CategoryDocument, error)
	FindManyByFilter(options findmanyoptions.FindManyOptions, id string) ([]*models.CategoryDocument, error)
}
