package category

type CategoryTreeNode struct {
	Id       string
	Name     string
	Children []*CategoryTreeNode
}
