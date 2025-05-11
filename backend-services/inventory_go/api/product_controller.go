package api

import (
	"errors"
	"github.com/gin-gonic/gin"
	"inventory_go/api/payloads"
	"inventory_go/infrastructure/repositories"
	"inventory_go/product"
	"inventory_go/product/mappers"
	"inventory_go/service"
	"net/http"
)

type ProductController struct {
	router  *gin.Engine
	service product.ProductService
}

func NewProductController(router *gin.Engine, service product.ProductService) *ProductController {
	return &ProductController{
		router:  router,
		service: service,
	}
}

func (controller *ProductController) ExposeEndpoints() {
	controller.Create()
	controller.UpdateName()
	controller.UpdatePrice()
	controller.UpdateImage()
	controller.UpdateDescription()
	controller.Delete()
	controller.FindOneById()
	controller.FindAll()
	controller.FindManyByName()
	controller.FindManyByCategory()
	controller.FindStock()
}

// CreateProduct godoc
// @Summary      Create a new product
// @Description  Creates a product with optional category assignment
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        product   body      payloads.CreateProductPayload  true  "Product payload"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product [post]
func (controller *ProductController) Create() {
	controller.router.POST("product", func(c *gin.Context) {
		var payload payloads.CreateProductPayload
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			return
		}
		_product := mappers.ProductPayloadToDomain(payload)
		err := controller.service.Create(_product)
		if err != nil {
			switch {
			case errors.Is(err, service.ErrIdShouldBeEmpty):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrCategoryNotFound):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, service.ErrProductValidationFailed):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusCreated, gin.H{"status": Success, "message": nil, "data": nil})
	})
}

// UpdateProductName godoc
// @Summary      Update product name
// @Description  Renames a product by ID
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        id        path      string             true  "Product ID"
// @Param        payload   body      payloads.UpdateProductNamePayload true  "New name"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product/name/{id} [put]
func (controller *ProductController) UpdateName() {
	controller.router.PUT("product/name/:id", func(c *gin.Context) {
		id := c.Param("id")
		var payload payloads.UpdateProductNamePayload
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
		}
		err := controller.service.UpdateName(id, payload.Name)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrProductNotFound):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, service.ErrProductValidationFailed):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "message": nil, "data": nil})
	})
}

// UpdateProductPrice godoc
// @Summary      Update product price
// @Description  Changes the price of a product by ID
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        id        path      string               true  "Product ID"
// @Param        payload   body      payloads.UpdatePricePayload true  "New price"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product/price/{id} [put]
func (controller *ProductController) UpdatePrice() {
	controller.router.PUT("product/price/:id", func(c *gin.Context) {
		id := c.Param("id")
		var payload payloads.UpdatePricePayload
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
		}
		err := controller.service.UpdatePrice(id, payload.Price)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrProductNotFound):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, service.ErrProductValidationFailed):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "message": nil, "data": nil})
	})
}

// UpdateProductImage godoc
// @Summary      Update product image
// @Description  Updates the image URL of a product by ID
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        id        path      string               true  "Product ID"
// @Param        payload   body      payloads.UpdateImagePayload  true  "Image URL"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product/image/{id} [put]
func (controller *ProductController) UpdateImage() {
	controller.router.PUT("product/image/:id", func(c *gin.Context) {
		id := c.Param("id")
		var payload payloads.UpdateImagePayload
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
		}
		err := controller.service.UpdateImage(id, payload.Image)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrProductNotFound):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "message": nil, "data": nil})
	})
}

// UpdateProductDescription godoc
// @Summary      Update product description
// @Description  Changes the description of a product by ID
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        id        path      string                       true  "Product ID"
// @Param        payload   body      payloads.UpdateDescriptionPayload    true  "New description"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product/description/{id} [put]
func (controller *ProductController) UpdateDescription() {
	controller.router.PUT("product/description/:id", func(c *gin.Context) {
		id := c.Param("id")
		var payload payloads.UpdateDescriptionPayload
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
		}
		err := controller.service.UpdateDescription(id, payload.Description)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrProductNotFound):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, service.ErrProductValidationFailed):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "message": nil, "data": nil})
	})
}

// DeleteProduct godoc
// @Summary      Delete a product
// @Description  Removes a product by ID
// @Tags         products
// @Produce      json
// @Param        id        path      string  true  "Product ID"
// @Success      200       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product/{id} [delete]
func (controller *ProductController) Delete() {
	controller.router.DELETE("product/:id", func(c *gin.Context) {
		id := c.Param("id")
		err := controller.service.Delete(id)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "message": nil, "data": nil})
	})
}

// FindProductById godoc
// @Summary      Get a product
// @Description  Retrieves a product by ID
// @Tags         products
// @Produce      json
// @Param        id        path      string  true  "Product ID"
// @Success      200       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product/{id} [get]
func (controller *ProductController) FindOneById() {
	controller.router.GET("product/:id", func(c *gin.Context) {
		id := c.Param("id")
		result, err := controller.service.FindById(id)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrProductNotFound):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": result, "message": nil})
	})
}

// ListProducts godoc
// @Summary      List all products
// @Description  Retrieves all products
// @Tags         products
// @Produce      json
// @Success      200       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product [get]
func (controller *ProductController) FindAll() {
	controller.router.GET("product", func(c *gin.Context) {
		result, err := controller.service.FindAll()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": result, "message": nil})
	})
}

// SearchProductsByName godoc
// @Summary      Search products by name
// @Description  Finds products matching a partial name
// @Tags         products
// @Produce      json
// @Param        name      path      string  true  "Partial name"
// @Success      200       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product/many/{name} [get]
func (controller *ProductController) FindManyByName() {
	controller.router.GET("product/many/:name", func(c *gin.Context) {
		name := c.Param("name")
		result, err := controller.service.FindManyByName(name)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": result, "message": nil})
	})
}

// ListProductsByCategory godoc
// @Summary      List products in a category
// @Description  Retrieves products by category ID
// @Tags         products
// @Produce      json
// @Param        category  path      string  true  "Category ID"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product/category/{category} [get]
func (controller *ProductController) FindManyByCategory() {
	controller.router.GET("product/category/:category", func(c *gin.Context) {
		category := c.Param("category")
		result, err := controller.service.FindManyByCategory(category)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": result, "message": nil})
	})
}

// GetProductStock godoc
// @Summary      Get product stock
// @Description  Retrieves stock level for a product by ID
// @Tags         products
// @Produce      json
// @Param        id        path      string  true  "Product ID"
// @Success      200       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /product/stock/{id} [get]
func (controller *ProductController) FindStock() {
	controller.router.GET("product/stock/:id", func(c *gin.Context) {
		id := c.Param("id")
		result, err := controller.service.FindStock(id)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrProductNotFound):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": result, "message": nil})
	})
}
