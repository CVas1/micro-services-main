package service

import (
	"errors"
	"inventory_go/category"
	findmanyoptions "inventory_go/category/enums"
	"inventory_go/category/mappers"
	"inventory_go/infrastructure/repositories"
	"log"
)

type CategoryServiceImpl struct {
	repository category.CategoryRepository
}

func NewCategoryService(repository category.CategoryRepository) *CategoryServiceImpl {
	return &CategoryServiceImpl{repository: repository}
}

func (service *CategoryServiceImpl) Create(category *category.Category) error {
	if category.GetId() != "" {
		return ErrIdShouldBeEmpty
	}

	// Rule 0: Each category should have a unique name
	_category, err := service.repository.FindByName(category.GetName())
	if err != nil && !errors.Is(err, repositories.ErrCategoryNotFound) {
		return err
	}

	if _category != nil {
		return ErrDuplicateCategoryName
	}

	if category.GetParentId() != "" {
		// Check if the parent category exists
		parentCategory, err := service.repository.GetById(category.GetParentId())
		if err != nil && !errors.Is(err, repositories.ErrCategoryNotFound) {
			return err
		}
		if parentCategory == nil {
			return ErrInvalidParentCategory
		}
	}

	err = service.repository.Save(category)
	return err
}

func (service *CategoryServiceImpl) Update(id string, name string) error {
	// Rule 0: Each category should have a unique name
	_category, err := service.repository.FindByName(name)
	if err != nil && !errors.Is(err, repositories.ErrCategoryNotFound) {
		return err
	}
	if _category != nil {
		return ErrDuplicateCategoryName
	}

	// Check if category exists
	_category, err = service.repository.GetById(id)
	if err != nil {
		return err
	}

	domain := mappers.ToDomain(_category)
	event, err := domain.Rename(name, true)

	if err != nil {
		return ErrInvalidCategoryName
	}

	// For now, log the event as nobody is listening
	log.Print(event)

	err = service.repository.Save(domain)
	return err
}

func (service *CategoryServiceImpl) Delete(id string) error {
	// Rule 1: A category cannot be deleted if it has subcategories
	subcategories, err := service.repository.FindManyByFilter(findmanyoptions.FindAllSubCategoriesById, id)
	if err != nil {
		return err
	}
	if len(subcategories) > 0 {
		return ErrCantDeleteCategoryWithSubcategories
	}
	err = service.repository.Delete(id)
	return err
}

func (service *CategoryServiceImpl) FindOneById(id string) (*category.Category, error) {
	_category, err := service.repository.GetById(id)
	if err != nil {
		return nil, err
	}
	domain := mappers.ToDomain(_category)
	return domain, nil
}

func (service *CategoryServiceImpl) FindAllSubCategoriesById(id string) ([]*category.Category, error) {
	// Check if category exists
	_, err := service.repository.GetById(id)
	if err != nil {
		return nil, err
	}

	subcategories, err := service.repository.FindManyByFilter(findmanyoptions.FindAllSubCategoriesById, id)
	if err != nil {
		return nil, err
	}
	var result []*category.Category
	for _, subcategory := range subcategories {
		result = append(result, mappers.ToDomain(subcategory))
	}
	return result, err
}

func (service *CategoryServiceImpl) FindAllParentCategories() ([]*category.Category, error) {
	categories, err := service.repository.FindManyByFilter(findmanyoptions.FindAllParents, "")
	if err != nil {
		return nil, err
	}
	var result []*category.Category
	for _, _category := range categories {
		result = append(result, mappers.ToDomain(_category))
	}
	return result, err
}
func (service *CategoryServiceImpl) FindAll() ([]*category.Category, error) {
	categories, err := service.repository.FindManyByFilter(findmanyoptions.FindAll, "")
	if err != nil {
		return nil, err
	}
	var result []*category.Category
	for _, _category := range categories {
		result = append(result, mappers.ToDomain(_category))
	}
	return result, err
}

func (service *CategoryServiceImpl) FindCategoryTree() ([]*category.CategoryTreeNode, error) {
	categories, err := service.FindAll()
	if err != nil {
		return nil, err
	}
	if len(categories) == 0 {
		return nil, ErrCategoryTreeIsEmpty
	}

	childrenMap := make(map[string][]*category.Category)

	for _, cat := range categories {
		pid := cat.GetParentId()
		childrenMap[pid] = append(childrenMap[pid], cat)
	}
	var result []*category.CategoryTreeNode
	for _, cat := range categories {
		if cat.GetParentId() != "" {
			// not a root
			continue
		}
		// get its children (may be nil but that's fine—empty slice)
		childCats := childrenMap[cat.GetId()]

		// convert []*Category → []*CategoryTreeNode if you want multi-level,
		// or store Category children directly if your TreeNode accepts that.
		var childNodes []*category.CategoryTreeNode
		for _, ch := range childCats {
			childNodes = append(childNodes, &category.CategoryTreeNode{
				Id:       ch.GetId(),
				Name:     ch.GetName(),
				Children: nil, // no grandchildren in this simple example
			})
		}

		node := &category.CategoryTreeNode{
			Id:       cat.GetId(),
			Name:     cat.GetName(),
			Children: childNodes,
		}
		result = append(result, node)
	}

	return result, nil
}
