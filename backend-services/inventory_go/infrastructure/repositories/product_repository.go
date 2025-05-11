package repositories

import (
	"context"
	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
	"inventory_go/infrastructure/models"
	"inventory_go/product"
	"inventory_go/product/enums"
	"inventory_go/product/mappers"
	"log"
	"regexp"
	"time"
)

type ProductRepositoryImpl struct {
	collection *mongo.Collection
}

func NewProductRepository(db *mongo.Database, collectionName string) *ProductRepositoryImpl {
	return &ProductRepositoryImpl{
		collection: db.Collection(collectionName),
	}
}

func (r *ProductRepositoryImpl) GetById(id string) (*models.ProductDocument, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	objectId, err := bson.ObjectIDFromHex(id)
	if err != nil {
		return nil, ErrInvalidId
	}

	var _product models.ProductDocument
	err = r.collection.FindOne(ctx, bson.M{"_id": objectId}).Decode(&_product)
	if err != nil {
		return nil, ErrProductNotFound
	}
	return &_product, nil
}

func (r *ProductRepositoryImpl) Save(product *product.Product) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	productDocument, err := mappers.ProductDomainToDocument(product)
	if err != nil {
		return ErrMappingError
	}

	if productDocument.Id.IsZero() {
		productDocument.Id = bson.NewObjectID()
		_, err = r.collection.InsertOne(ctx, productDocument)
		if err != nil {
			return ErrDuplicateKey
		}
		return nil
	}

	filter := bson.M{"_id": productDocument.Id}
	update := bson.M{"$set": productDocument}
	_, err = r.collection.UpdateOne(ctx, filter, update, options.UpdateOne().SetUpsert(true))
	if err != nil {
		return err
	}
	return nil
}

func (r *ProductRepositoryImpl) Delete(id string) error {
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
		return ErrProductNotFound
	}
	return err
}

func (r *ProductRepositoryImpl) FindManyByFilter(option findmanyproductoptions.FindManyProductOptions, name string, categoryId string) ([]*models.ProductDocument, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var cursor *mongo.Cursor
	var err error

	if option == findmanyproductoptions.FindAll {
		cursor, err = r.collection.Find(ctx, bson.M{})
	} else if option == findmanyproductoptions.FindByName && name != "" {
		escaped := regexp.QuoteMeta(name)
		filter := bson.M{"name": bson.M{
			"$regex": bson.Regex{Pattern: escaped, Options: "i"},
		}}
		cursor, err = r.collection.Find(ctx, filter)
	} else if option == findmanyproductoptions.FindByCategory && categoryId != "" {
		objectId, err := bson.ObjectIDFromHex(categoryId)
		if err != nil {
			return nil, ErrInvalidId
		}
		filter := bson.M{"category_id": bson.M{"$eq": objectId}}
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

	var productDocuments []*models.ProductDocument
	if err := cursor.All(ctx, &productDocuments); err != nil {
		log.Println("Error reading products from cursor:", err)
		return nil, err
	}
	return productDocuments, nil
}

func (r *ProductRepositoryImpl) GetStock(id string) (int, error) {
	_product, err := r.GetById(id)
	if err != nil {
		return 0, err
	}
	return _product.Stock, nil
}
