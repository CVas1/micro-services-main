package mappers

import (
	"go.mongodb.org/mongo-driver/v2/bson"
	"inventory_go/api/payloads"
	"inventory_go/infrastructure/models"
	"inventory_go/product"
)

func ProductDomainToDocument(product *product.Product) (*models.ProductDocument, error) {
	var id bson.ObjectID
	var err error

	if product.GetId() != "" {
		id, err = bson.ObjectIDFromHex(product.GetId())
		if err != nil {
			return nil, err
		}
	}

	var categoryId bson.ObjectID
	if product.GetCategoryId() != "" {
		categoryId, err = bson.ObjectIDFromHex(product.GetCategoryId())
		if err != nil {
			return nil, err
		}
	}

	return &models.ProductDocument{
		Id:          id,
		CategoryId:  categoryId,
		Name:        product.GetName(),
		Price:       product.GetPrice(),
		Stock:       product.GetStock(),
		VendorId:    product.GetVendorId(),
		Image:       product.GetImage(),
		Description: product.GetDescription(),
	}, nil
}

func ProductDocumentToDomain(document *models.ProductDocument) *product.Product {
	var id string
	if !bson.ObjectID.IsZero(document.Id) {
		id = document.Id.Hex()
	}

	var categoryId string
	if !bson.ObjectID.IsZero(document.CategoryId) {
		categoryId = document.CategoryId.Hex()
	}
	return product.NewProduct(id, document.Name, document.Price, document.Stock, document.VendorId, document.Image, categoryId, document.Description)

}

func ProductPayloadToDomain(payload payloads.CreateProductPayload) *product.Product {
	return product.NewProduct("", payload.Name, payload.Price, payload.Stock, payload.VendorId, payload.Image, payload.CategoryId, payload.Description)
}
