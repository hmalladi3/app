package main

import (
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"gorm.io/gorm"
)

var db *gorm.DB

func init() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: .env file not found")
	}
}

func setupRouter() *gin.Engine {
	r := gin.Default()

	// Enable CORS
	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "http://localhost:8082")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "*")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// Account routes
	r.POST("/api/accounts", createAccount)
	r.POST("/api/login", login)
	r.GET("/api/accounts/:account_id", getAccount)
	r.PUT("/api/accounts/:account_id", updateAccount)
	r.DELETE("/api/accounts/:account_id", deleteAccount)

	// Service routes
	r.POST("/api/services", createService)
	r.GET("/api/services/:service_id", getService)
	r.GET("/api/accounts/:account_id/services", getAccountServices)
	r.GET("/api/services", searchServices)
	r.DELETE("/api/services/:service_id", deleteService)

	// Review routes
	r.POST("/api/services/:service_id/reviews", createReview)
	r.GET("/api/services/:service_id/reviews", getServiceReviews)
	r.GET("/api/services/:service_id/rating", getServiceRating)
	r.DELETE("/api/reviews/:review_id", deleteReview)

	// Hashtag routes
	r.POST("/api/accounts/:account_id/hashtags", addHashtags)
	r.GET("/api/accounts/:account_id/hashtags", getAccountHashtags)
	r.GET("/api/hashtags/search", searchHashtags)
	r.GET("/api/hashtags/:tag/accounts", getAccountsByHashtag)
	r.DELETE("/api/accounts/:account_id/hashtags/:tag", removeHashtag)

	// Search routes
	r.GET("/api/search", searchAll)
	r.GET("/api/search/advanced", advancedSearch)

	return r
}

func main() {
	// Initialize database connection
	initDB()

	// Set up router
	r := setupRouter()

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}
	r.Run(":" + port)
}
