package main

import (
	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
	"inventory_go/api"
	_ "inventory_go/docs"
	"inventory_go/infrastructure"
	"inventory_go/infrastructure/repositories"
	"inventory_go/rabbitmq"
	"inventory_go/service"
	"log"
	"os"
	"net/http"
)

func main() {

	// Connect to mongodb
	client, err := infrastructure.Connect()
	if err != nil {
		os.Exit(1)
	}

	// Get the database
	db := client.Database("inventory")

	// Get repositories
	categoryCollectionName := os.Getenv("CATEGORY_COLLECTION")
	if categoryCollectionName == "" {
		categoryCollectionName = "categories"
	}
	productCollectionName := os.Getenv("PRODUCT_COLLECTION")
	if productCollectionName == "" {
		productCollectionName = "products"
	}

	transactionCollectionName := os.Getenv("TRANSACTION_COLLECTION")
	if transactionCollectionName == "" {
		transactionCollectionName = "transactions"
	}

	categoryRepository := repositories.NewCategoryRepository(db, categoryCollectionName)
	productRepository := repositories.NewProductRepository(db, productCollectionName)
	transactionRepository := repositories.NewTransactionRepository(db, transactionCollectionName)

	// Get services
	categoryService := service.NewCategoryService(categoryRepository)
	productService := service.NewProductService(productRepository, categoryRepository, transactionRepository)

	// Connect to rabbitmq
	rabbitmqConnectionString := os.Getenv("RABBITMQ_URL")
	if rabbitmqConnectionString == "" {
		rabbitmqConnectionString = "amqp://guest:guest@localhost:5672"
	}

	connection, err := rabbitmq.Connect(rabbitmqConnectionString)
	if err != nil {
		log.Fatal(err)
	}
	defer func() {
		maxTries := 10
		err = connection.Close()
		for err != nil && maxTries > 0 {
			err = connection.Close()
			maxTries--
		}
	}()

	// Set up consumer
	productQueue := os.Getenv("PRODUCT_QUEUE")
	if productQueue == "" {
		productQueue = "products_queue"
	}
	consumer, err := rabbitmq.NewConsumer(connection, productQueue)
	if err != nil {
		log.Fatal(err)
	}

	// Set up publisher
	orchestrationQueue := os.Getenv("ORCHESTRATION_QUEUE")
	if orchestrationQueue == "" {
		orchestrationQueue = "orchestration_queue"
	}
	publisher, err := rabbitmq.NewPublisher(connection, orchestrationQueue)

	if err != nil {
		log.Fatal(err)
	}

	// Handle delivered packages
	rabbitmq.HandleConsumer(consumer, productService, publisher)

	// Set up router
	router := gin.Default()

	router.Use(gin.Recovery())
	router.Use(gin.Logger())

	// Apply the CORS middleware globally
	router.Use(CORSMiddleware())

	// Expose endpoints
	categoryController := api.NewCategoryController(router, categoryService)
	categoryController.ExposeEndpoints()

	productController := api.NewProductController(router, productService)
	productController.ExposeEndpoints()

	router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// Run the router on port 9292
	err = router.Run(":9292")
	if err != nil {
		log.Fatal("Server failed to start:", err)
	}
}

func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Allow all origins
		c.Header("Access-Control-Allow-Origin", "*")

		// Allow all HTTP methods
		c.Header("Access-Control-Allow-Methods", "*")

		// Allow all headers
		c.Header("Access-Control-Allow-Headers", "*") 

		// Handle preflight requests (OPTIONS method)
		if c.Request.Method == http.MethodOptions {
			c.AbortWithStatus(http.StatusOK)
			return
		}

		// Continue with the request
		c.Next()
	}
}
