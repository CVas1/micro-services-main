package service

import (
	"errors"
	"inventory_go/category"
	"inventory_go/product"
	findmanyproductoptions "inventory_go/product/enums"
	"inventory_go/product/mappers"
	"inventory_go/transaction"
)

type ProductServiceImpl struct {
	repository            product.ProductRepository
	categoryRepository    category.CategoryRepository
	transactionRepository transaction.TransactionRepository
}

func NewProductService(repository product.ProductRepository, categoryRepository category.CategoryRepository, transactionRepository transaction.TransactionRepository) *ProductServiceImpl {
	return &ProductServiceImpl{repository: repository, categoryRepository: categoryRepository, transactionRepository: transactionRepository}
}

func (service *ProductServiceImpl) Create(product *product.Product) error {
	if product.GetId() != "" {
		return ErrIdShouldBeEmpty
	}
	if product.GetCategoryId() != "" {
		_, err := service.categoryRepository.GetById(product.GetCategoryId())
		if err != nil {
			return err
		}
	}

	err := product.ValidateProduct()
	if err != nil {
		return ErrProductValidationFailed
	}

	// later there can be a vendor id check from authentication service
	err = service.repository.Save(product)
	return err
}

func (service *ProductServiceImpl) UpdateName(id string, name string) error {
	document, err := service.repository.GetById(id)
	if err != nil {
		return err
	}
	_product := mappers.ProductDocumentToDomain(document)

	err = _product.Rename(name)
	if err != nil {
		return ErrProductValidationFailed
	}
	err = service.repository.Save(_product)
	return err
}

func (service *ProductServiceImpl) UpdatePrice(id string, price float64) error {
	document, err := service.repository.GetById(id)
	if err != nil {
		return err
	}
	_product := mappers.ProductDocumentToDomain(document)
	err = _product.Reprice(price)
	if err != nil {
		return ErrProductValidationFailed
	}
	err = service.repository.Save(_product)
	return err
}

func (service *ProductServiceImpl) UpdateImage(id string, image string) error {
	document, err := service.repository.GetById(id)
	if err != nil {
		return err
	}
	_product := mappers.ProductDocumentToDomain(document)
	_product.UpdateImage(image)

	err = service.repository.Save(_product)
	return err
}

func (service *ProductServiceImpl) UpdateDescription(id string, description string) error {
	document, err := service.repository.GetById(id)
	if err != nil {
		return err
	}
	_product := mappers.ProductDocumentToDomain(document)
	err = _product.Redescribe(description)
	if err != nil {
		return ErrProductValidationFailed
	}
	err = service.repository.Save(_product)
	return err
}

func (service *ProductServiceImpl) Delete(id string) error {
	err := service.repository.Delete(id)
	return err
}

func (service *ProductServiceImpl) FindById(id string) (*product.Product, error) {
	document, err := service.repository.GetById(id)
	if err != nil {
		return nil, err
	}
	_product := mappers.ProductDocumentToDomain(document)
	return _product, nil
}

func (service *ProductServiceImpl) FindAll() ([]*product.Product, error) {
	documents, err := service.repository.FindManyByFilter(findmanyproductoptions.FindAll, "", "")
	if err != nil {
		return nil, err
	}
	var products []*product.Product
	for _, document := range documents {
		products = append(products, mappers.ProductDocumentToDomain(document))
	}
	return products, err
}

func (service *ProductServiceImpl) FindManyByName(name string) ([]*product.Product, error) {
	documents, err := service.repository.FindManyByFilter(findmanyproductoptions.FindByName, name, "")
	if err != nil {
		return nil, err
	}
	var products []*product.Product
	for _, document := range documents {
		products = append(products, mappers.ProductDocumentToDomain(document))
	}
	return products, err
}

func (service *ProductServiceImpl) FindManyByCategory(categoryId string) ([]*product.Product, error) {
	documents, err := service.repository.FindManyByFilter(findmanyproductoptions.FindByCategory, "", categoryId)
	if err != nil {
		return nil, err
	}
	var products []*product.Product
	for _, document := range documents {
		products = append(products, mappers.ProductDocumentToDomain(document))
	}
	return products, err
}

func (service *ProductServiceImpl) FindStock(id string) (int, error) {
	stock, err := service.repository.GetStock(id)
	return stock, err
}

func (service *ProductServiceImpl) ReduceStock(id string, quantity int, transactionId string) error {
	document, err := service.repository.GetById(id)
	if err != nil {
		return err
	}
	if quantity < 0 || quantity > document.Stock {
		return errors.New("invalid quantity")
	}

	stock := document.Stock - quantity

	_product := mappers.ProductDocumentToDomain(document)
	_product.UpdateStock(stock)

	err = service.transactionRepository.InsertTransaction(&transaction.Transaction{TransactionId: transactionId, Stock: quantity, ProductId: id})
	if err != nil {
		return err
	}

	err = service.repository.Save(_product)
	return err
}

func (service *ProductServiceImpl) IncreaseStock(id string, quantity int) error {
	document, err := service.repository.GetById(id)
	if err != nil {
		return err
	}
	if quantity < 0 {
		return errors.New("invalid quantity")
	}
	stock := document.Stock + quantity

	_product := mappers.ProductDocumentToDomain(document)
	_product.UpdateStock(stock)

	err = service.repository.Save(_product)
	return err
}

func (service *ProductServiceImpl) StockRollback(transactionId string) error {
	_transaction, err := service.transactionRepository.GetByTransactionId(transactionId)
	if err != nil {
		return err
	}

	if _transaction.RolledBack {
		return errors.New("transaction is already rolled back")
	}

	err = service.IncreaseStock(_transaction.ProductId, _transaction.Stock)
	if err != nil {
		return err
	}
	err = service.transactionRepository.SetRolledBack(_transaction.TransactionId)
	if err != nil {
		return err
	}
	return nil
}
