package payloads

type CreateCategoryPayload struct {
	Name     string `json:"name" binding:"required"`
	ParentId string `json:"parent_id"`
}
