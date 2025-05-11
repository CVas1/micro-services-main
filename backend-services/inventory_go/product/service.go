package product

type ProductService interface {
	Create(product *Product) error
	UpdateName(id string, name string) error
	UpdatePrice(id string, price float64) error
	UpdateImage(id string, image string) error
	UpdateDescription(id string, description string) error
	Delete(id string) error
	FindById(id string) (*Product, error)
	FindAll() ([]*Product, error)
	FindManyByName(name string) ([]*Product, error)
	FindManyByCategory(categoryId string) ([]*Product, error)
	FindStock(id string) (int, error)
	ReduceStock(id string, quantity int, transactionId string) error
	IncreaseStock(id string, quantity int) error
	StockRollback(transactionId string) error
}
