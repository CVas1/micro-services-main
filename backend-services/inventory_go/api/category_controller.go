package api

import (
	"errors"
	"github.com/gin-gonic/gin"
	"inventory_go/api/payloads"
	"inventory_go/category"
	"inventory_go/category/mappers"
	"inventory_go/infrastructure/repositories"
	"inventory_go/service"
	"net/http"
)

type CategoryController struct {
	router  *gin.Engine
	service category.CategoryService
}

func NewCategoryController(router *gin.Engine, service category.CategoryService) *CategoryController {
	return &CategoryController{
		router:  router,
		service: service,
	}
}

func (controller *CategoryController) ExposeEndpoints() {
	controller.CreateCategory()
	controller.UpdateCategory()
	controller.DeleteCategory()
	controller.FindOneById()
	controller.FindAllCategories()
	controller.FindAllParentCategories()
	controller.FindSubcategoriesById()
	controller.FindCategoryTree()
}

// CreateCategory godoc
// @Summary      Create a new category
// @Description  Creates a category with a unique name and optional parent
// @Tags         categories
// @Accept       json
// @Produce      json
// @Param        category  body      payloads.CreateCategoryPayload  true  "Category payload"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      409       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /category [post]
func (controller *CategoryController) CreateCategory() {
	controller.router.POST("/category", func(c *gin.Context) {
		var payload payloads.CreateCategoryPayload
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			return
		}
		_category := mappers.PayloadToDomain(payload)
		err := controller.service.Create(_category)
		if err != nil {
			switch {
			case errors.Is(err, service.ErrIdShouldBeEmpty):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrCategoryNotFound):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, service.ErrDuplicateCategoryName):
				c.JSON(http.StatusConflict, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, service.ErrInvalidParentCategory):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusCreated, gin.H{"status": Success, "data": nil, "message": nil})
	})
}

// UpdateCategory godoc
// @Summary      Rename an existing category
// @Description  Updates the name of a category by ID
// @Tags         categories
// @Accept       json
// @Produce      json
// @Param        id        path      string              true  "Category ID"
// @Param        payload   body      payloads.UpdateCategoryPayload true  "New name"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      409       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /category/{id} [put]
func (controller *CategoryController) UpdateCategory() {
	controller.router.PUT("/category/:id", func(c *gin.Context) {
		id := c.Param("id")
		var payload payloads.UpdateCategoryPayload
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			return
		}
		err := controller.service.Update(id, payload.Name)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrCategoryNotFound):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, service.ErrDuplicateCategoryName):
				c.JSON(http.StatusConflict, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, service.ErrInvalidCategoryName):
				c.JSON(http.StatusConflict, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": nil, "message": nil})
	})
}

// DeleteCategory godoc
// @Summary      Delete a category
// @Description  Deletes a category by ID if no subcategories exist
// @Tags         categories
// @Produce      json
// @Param        id        path      string  true  "Category ID"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      409       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /category/{id} [delete]
func (controller *CategoryController) DeleteCategory() {
	controller.router.DELETE("/category/:id", func(c *gin.Context) {
		id := c.Param("id")
		err := controller.service.Delete(id)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, service.ErrCantDeleteCategoryWithSubcategories):
				c.JSON(http.StatusConflict, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": nil, "message": nil})
	})
}

// FindOneById godoc
// @Summary      Get a category
// @Description  Retrieves a category by ID
// @Tags         categories
// @Produce      json
// @Param        id        path      string  true  "Category ID"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /category/{id} [get]
func (controller *CategoryController) FindOneById() {
	controller.router.GET("/category/:id", func(c *gin.Context) {
		id := c.Param("id")
		result, err := controller.service.FindOneById(id)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrInvalidId):
				c.JSON(http.StatusBadRequest, gin.H{"status": Error, "message": err.Error(), "data": nil})
			case errors.Is(err, repositories.ErrCategoryNotFound):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": result, "message": nil})
	})
}

// FindSubcategoriesById godoc
// @Summary      List subcategories
// @Description  Retrieves direct subcategories for a given category ID
// @Tags         categories
// @Produce      json
// @Param        id        path      string  true  "Category ID"
// @Success      200       {object}  map[string]interface{}
// @Failure      400       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /category/{id}/subcategories [get]
func (controller *CategoryController) FindSubcategoriesById() {
	controller.router.GET("/category/:id/subcategories", func(c *gin.Context) {
		id := c.Param("id")
		result, err := controller.service.FindAllSubCategoriesById(id)
		if err != nil {
			switch {
			case errors.Is(err, repositories.ErrCategoryNotFound):
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

// FindAllParentCategories godoc
// @Summary      List root categories
// @Description  Retrieves categories without a parent
// @Tags         categories
// @Produce      json
// @Success      200       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /category/parents [get]
func (controller *CategoryController) FindAllParentCategories() {
	controller.router.GET("/category/parents", func(c *gin.Context) {
		result, err := controller.service.FindAllParentCategories()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": result, "message": nil})
	})
}

// FindAllCategories godoc
// @Summary      List all categories
// @Description  Retrieves all categories
// @Tags         categories
// @Produce      json
// @Success      200       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /category [get]
func (controller *CategoryController) FindAllCategories() {
	controller.router.GET("/category", func(c *gin.Context) {
		result, err := controller.service.FindAll()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": result, "message": nil})
	})
}

// FindCategoryTree godoc
// @Summary      Category tree
// @Description  Retrieves the full category tree
// @Tags         categories
// @Produce      json
// @Success      200       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]interface{}
// @Failure      500       {object}  map[string]interface{}
// @Router       /category/tree [get]
func (controller *CategoryController) FindCategoryTree() {
	controller.router.GET("/category/tree", func(c *gin.Context) {
		result, err := controller.service.FindCategoryTree()
		if err != nil {
			switch {
			case errors.Is(err, service.ErrCategoryTreeIsEmpty):
				c.JSON(http.StatusNotFound, gin.H{"status": Error, "message": err.Error(), "data": nil})
			default:
				c.JSON(http.StatusInternalServerError, gin.H{"status": Error, "message": err.Error(), "data": nil})
			}
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": Success, "data": result, "message": nil})
	})
}
