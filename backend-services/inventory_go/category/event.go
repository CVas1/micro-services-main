package category

type DomainEvent interface {
	EventName() string
}
