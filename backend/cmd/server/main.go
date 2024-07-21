// backend/cmd/server/main.go
package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	v1 "github.com/mcopur/sap-assist/internal/api/v1"
	"github.com/mcopur/sap-assist/internal/config"
	"github.com/mcopur/sap-assist/internal/database"
	"github.com/mcopur/sap-assist/internal/middleware"
	"github.com/mcopur/sap-assist/internal/service"
	httpSwagger "github.com/swaggo/http-swagger"
	"golang.org/x/time/rate"
)

// @title SAP Assist API
// @version 1.0
// @description This is a sample server for SAP Assist application.
// @termsOfService http://swagger.io/terms/

// @contact.name API Support
// @contact.url http://www.swagger.io/support
// @contact.email support@swagger.io

// @license.name Apache 2.0
// @license.url http://www.apache.org/licenses/LICENSE-2.0.html

// @host localhost:8080
// @BasePath /api/v1

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	db, err := database.InitDB(cfg)
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	repo := database.NewRepository(db)
	nlpService := service.NewNLPService("http://localhost:5000") // NLP servisi URL'sini buraya girin
	svc := service.NewService(repo, nlpService)                  // NLPService'i burada atayın

	limiter := middleware.NewIPRateLimiter(rate.Limit(5), 10)

	corsOptions := handlers.CORS(
		handlers.AllowedOrigins([]string{"http://localhost:5173"}),
		handlers.AllowedMethods([]string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}),
		handlers.AllowedHeaders([]string{"Content-Type", "Authorization"}),
		handlers.AllowCredentials(),
	)

	r := mux.NewRouter()

	// Middleware'leri uygulama
	r.Use(func(next http.Handler) http.Handler {
		return middleware.Logging(next.ServeHTTP)
	})
	r.Use(corsOptions)
	r.Use(func(next http.Handler) http.Handler {
		return middleware.RateLimit(limiter)(next.ServeHTTP)
	})

	// OPTIONS metodunu ele almak için handler
	r.Methods("OPTIONS").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	// Swagger
	r.PathPrefix("/swagger/").Handler(httpSwagger.WrapHandler)

	// API v1
	apiV1 := v1.NewAPIv1(svc)
	apiV1Router := r.PathPrefix("/api/v1").Subrouter()
	apiV1.RegisterRoutes(apiV1Router)

	log.Printf("Starting server on :%d", cfg.ServerPort)
	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%d", cfg.ServerPort), handlers.CompressHandler(r)))
}
