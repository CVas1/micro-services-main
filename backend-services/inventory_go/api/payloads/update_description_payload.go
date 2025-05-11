package payloads

type UpdateDescriptionPayload struct {
	Description string `json:"description" binding:"required"`
}
