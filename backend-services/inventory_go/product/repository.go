package product

import (
	"inventory_go/infrastructure/models"
	"inventory_go/product/enums"
)

type ProductRepository interface {
	GetById(id string) (*models.ProductDocument, error)
	Save(product *Product) error
	Delete(id string) error
	FindManyByFilter(options findmanyproductoptions.FindManyProductOptions, name string, categoryId string) ([]*models.ProductDocument, error)
	GetStock(id string) (int, error)
}
