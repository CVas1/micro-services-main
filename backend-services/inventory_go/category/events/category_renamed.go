package category

import "time"

type CategoryRenamed struct {
	Id         string
	OldName    string
	NewName    string
	OccurredAt time.Time
}

func (e CategoryRenamed) EventName() string { return "CategoryRenamed" }
