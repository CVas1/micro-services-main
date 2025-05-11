package category

type CategoryService interface {
	Create(category *Category) error
	Update(id string, name string) error
	Delete(id string) error
	FindOneById(id string) (*Category, error)
	FindAllSubCategoriesById(id string) ([]*Category, error)
	FindAllParentCategories() ([]*Category, error)
	FindAll() ([]*Category, error)
	FindCategoryTree() ([]*CategoryTreeNode, error)
}
