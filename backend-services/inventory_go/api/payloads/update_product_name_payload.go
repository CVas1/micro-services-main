package payloads

type UpdateProductNamePayload struct {
	Name string `json:"name" binding:"required"`
}
