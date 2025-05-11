package findmanyproductoptions

type FindManyProductOptions int

const (
	FindAll FindManyProductOptions = iota
	FindByName
	FindByCategory
)
