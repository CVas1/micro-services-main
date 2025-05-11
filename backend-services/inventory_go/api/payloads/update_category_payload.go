package payloads

type UpdateCategoryPayload struct {
	Name string `json:"name" binding:"required"`
}
