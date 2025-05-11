package payloads

type CreateProductPayload struct {
	Name        string  `json:"name" binding:"required"`
	Price       float64 `json:"price" binding:"required"`
	Stock       int     `json:"stock" binding:"required"`
	VendorId    string  `json:"vendor_id" binding:"required"`
	Image       string  `json:"image" binding:""`
	CategoryId  string  `json:"category_id" binding:""`
	Description string  `json:"description" binding:""`
}
