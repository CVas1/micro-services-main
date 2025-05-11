package mappers

import (
	"go.mongodb.org/mongo-driver/v2/bson"
	"inventory_go/api/payloads"
	"inventory_go/category"
	"inventory_go/infrastructure/models"
)

func ToDocument(category *category.Category) (*models.CategoryDocument, error) {
	var id bson.ObjectID
	var err error
	if category.GetId() != "" {
		id, err = bson.ObjectIDFromHex(category.GetId())
		if err != nil {
			return nil, err
		}
	}

	var parentId bson.ObjectID
	if category.GetParentId() != "" {
		parentId, err = bson.ObjectIDFromHex(category.GetParentId())
		if err != nil {
			return nil, err
		}
	}

	return &models.CategoryDocument{
		Id:       id,
		Name:     category.GetName(),
		ParentId: parentId,
	}, nil
}

func ToDomain(document *models.CategoryDocument) *category.Category {
	var id string
	if !bson.ObjectID.IsZero(document.Id) {
		id = document.Id.Hex()
	}

	var parentId string
	if !bson.ObjectID.IsZero(document.ParentId) {
		parentId = document.ParentId.Hex()
	}
	return category.NewCategory(id, document.Name, parentId)
}

func PayloadToDomain(payload payloads.CreateCategoryPayload) *category.Category {
	return category.NewCategory("", payload.Name, payload.ParentId)
}
