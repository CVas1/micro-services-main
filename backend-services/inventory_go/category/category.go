package category

import (
	"errors"
	"inventory_go/category/events"
	"time"
)

type Category struct {
	Id       string
	Name     string
	ParentId string
}

func NewCategory(id string, name string, parentId string) *Category {
	return &Category{Id: id, Name: name, ParentId: parentId}
}

func (c *Category) Rename(newName string, isNameUnique bool) (DomainEvent, error) {
	if !isNameUnique {
		return nil, errors.New("name is not unique")
	}
	if newName == "" {
		return nil, errors.New("name is empty")
	}
	oldName := c.Name
	c.Name = newName
	return category.CategoryRenamed{Id: c.Id, OldName: oldName, NewName: c.Name, OccurredAt: time.Now()}, nil
}

func (c *Category) GetId() string       { return c.Id }
func (c *Category) GetName() string     { return c.Name }
func (c *Category) GetParentId() string { return c.ParentId }
