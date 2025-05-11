package repositories

import (
	"context"
	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
	"inventory_go/category"
	findmanyoptions "inventory_go/category/enums"
	"inventory_go/category/mappers"
	"inventory_go/infrastructure/models"
	"log"
	"time"
)

type CategoryRepositoryImpl struct {
	collection *mongo.Collection
}

func NewCategoryRepository(db *mongo.Database, collectionName string) *CategoryRepositoryImpl {
	return &CategoryRepositoryImpl{
		collection: db.Collection(collectionName),
	}
}

func (r *CategoryRepositoryImpl) GetById(id string) (*models.CategoryDocument, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	objectId, err := bson.ObjectIDFromHex(id)
	if err != nil {
		return nil, ErrInvalidId
	}

	var _category models.CategoryDocument
	err = r.collection.FindOne(ctx, bson.M{"_id": objectId}).Decode(&_category)
	if err != nil {
		return nil, ErrCategoryNotFound

	}
	return &_category, nil
}

func (r *CategoryRepositoryImpl) Save(category *category.Category) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	categoryDocument, err := mappers.ToDocument(category)
	if err != nil {
		return ErrMappingError
	}

	if categoryDocument.Id.IsZero() {
		categoryDocument.Id = bson.NewObjectID()
		_, err = r.collection.InsertOne(ctx, categoryDocument)
		if err != nil {
			return ErrDuplicateKey
		}
		return nil
	}

	filter := bson.M{"_id": categoryDocument.Id}
	update := bson.M{"$set": categoryDocument}
	_, err = r.collection.UpdateOne(ctx, filter, update, options.UpdateOne().SetUpsert(true))
	if err != nil {
		return err
	}
	return nil
}

func (r *CategoryRepositoryImpl) Delete(id string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	objectId, err := bson.ObjectIDFromHex(id)
	if err != nil {
		return ErrInvalidId
	}

	res, err := r.collection.DeleteOne(ctx, bson.M{"_id": objectId})
	if err != nil {
		return err
	}

	if res.DeletedCount == 0 {
		return ErrCategoryNotFound
	}
	return err
}

func (r *CategoryRepositoryImpl) FindByName(name string) (*models.CategoryDocument, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var _category models.CategoryDocument
	err := r.collection.FindOne(ctx, bson.M{"name": name}).Decode(&_category)

	if err != nil {
		return nil, ErrCategoryNotFound
	}
	return &_category, nil
}

func (r *CategoryRepositoryImpl) FindManyByFilter(option findmanyoptions.FindManyOptions, id string) ([]*models.CategoryDocument, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var cursor *mongo.Cursor
	var err error

	if option == findmanyoptions.FindAll {
		cursor, err = r.collection.Find(ctx, bson.M{})
	} else if option == findmanyoptions.FindAllParents {
		filter := bson.M{"parent_id": bson.M{"$eq": bson.NilObjectID}}
		cursor, err = r.collection.Find(ctx, filter)
	} else if option == findmanyoptions.FindAllSubCategoriesById && id != "" {
		objectId, err := bson.ObjectIDFromHex(id)
		if err != nil {
			return nil, ErrInvalidId
		}
		filter := bson.M{"parent_id": bson.M{"$eq": objectId}}

		cursor, err = r.collection.Find(ctx, filter)
	} else {
		return nil, ErrInvalidOption
	}

	if err != nil {
		return nil, err
	}

	defer func(cursor *mongo.Cursor, ctx context.Context) {
		maxTries := 10
		err := cursor.Close(ctx)
		for err != nil && maxTries > 0 {
			err = cursor.Close(ctx)
			maxTries--
		}
	}(cursor, ctx)

	var categories []*models.CategoryDocument
	if err := cursor.All(ctx, &categories); err != nil {
		log.Println("Error reading categories from cursor:", err)
		return nil, err
	}

	return categories, nil
}
