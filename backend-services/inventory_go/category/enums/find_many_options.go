package enums

type FindManyOptions int

const (
	FindAll FindManyOptions = iota
	FindAllParents
	FindAllSubCategoriesById
)
