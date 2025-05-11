package payloads

type UpdateImagePayload struct {
	Image string `json:"description" binding:"required"`
}
