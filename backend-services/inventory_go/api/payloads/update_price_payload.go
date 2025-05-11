package payloads

type UpdatePricePayload struct {
	Price float64 `json:"price" binding:"required"`
}
