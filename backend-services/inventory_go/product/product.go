package product

import "errors"

type Product struct {
	Id          string
	Name        string
	Price       float64
	Stock       int
	VendorId    string
	Image       string
	CategoryId  string
	Description string
}

func NewProduct(id string, name string, price float64, stock int, vendorId string, image string, categoryId string, description string) *Product {
	return &Product{Id: id, Name: name, Price: price, Stock: stock, VendorId: vendorId, Image: image, CategoryId: categoryId, Description: description}
}

func (p *Product) Rename(name string) error {
	if name == p.Name {
		return errors.New("product name hasn't changed")
	}
	if name == "" {
		return errors.New("name cannot be empty")
	}
	p.Name = name
	return nil
}

func (p *Product) Reprice(price float64) error {
	if price <= 0 {
		return errors.New("price must be greater than zero")
	}
	p.Price = price
	return nil
}

func (p *Product) Redescribe(description string) error {
	if description == "" {
		return errors.New("description cannot be empty")
	}
	p.Description = description
	return nil
}

func (p *Product) UpdateImage(image string) {
	p.Image = image
}

func (p *Product) UpdateStock(stock int) {
	p.Stock = stock
}

func (p *Product) ValidateProduct() error {
	if p.GetName() == "" {
		return errors.New("name is required")
	}
	if p.GetPrice() <= 0 {
		return errors.New("price is required")
	}
	if p.GetStock() <= 0 {
		return errors.New("stock is required")
	}
	if p.GetVendorId() == "" {
		return errors.New("vendorId is required")
	}
	if p.GetDescription() == "" {
		return errors.New("description is required")
	}
	return nil
}
func (p *Product) GetId() string          { return p.Id }
func (p *Product) GetName() string        { return p.Name }
func (p *Product) GetPrice() float64      { return p.Price }
func (p *Product) GetStock() int          { return p.Stock }
func (p *Product) GetVendorId() string    { return p.VendorId }
func (p *Product) GetImage() string       { return p.Image }
func (p *Product) GetCategoryId() string  { return p.CategoryId }
func (p *Product) GetDescription() string { return p.Description }
