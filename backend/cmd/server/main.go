package main

import (
	"fmt"
	"log"
	"net/http"

	"time"

	"github.com/go-redis/redis/v8"
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	v1 "github.com/mcopur/sap-assist/internal/api/v1"
	"github.com/mcopur/sap-assist/internal/config"
	"github.com/mcopur/sap-assist/internal/database"
	"github.com/mcopur/sap-assist/internal/middleware"
	"github.com/mcopur/sap-assist/internal/service"
	httpSwagger "github.com/swaggo/http-swagger"
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

	// Redis istemcisini oluşturun
	redisClient := redis.NewClient(&redis.Options{
		Addr: cfg.RedisAddr,
	})

	// RateLimiter'ı oluşturun
	limiter := middleware.NewRateLimiter(redisClient, 100, time.Minute)
	repo := database.NewRepository(db)
	nlpService := service.NewNLPService(cfg.NLPServiceURL)
	sapConfig := &service.SAPConfig{
		BaseURL:      cfg.SAPBaseURL,
		ClientID:     cfg.SAPClientID,
		ClientSecret: cfg.SAPClientSecret,
	}
	svc := service.NewService(repo, nlpService, sapConfig)

	corsOptions := handlers.CORS(
		handlers.AllowedOrigins([]string{cfg.AllowedOrigin}),
		handlers.AllowedMethods([]string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}),
		handlers.AllowedHeaders([]string{"Content-Type", "Authorization"}),
		handlers.AllowCredentials(),
	)

	r := mux.NewRouter()

	r.Use(middleware.Logging)
	r.Use(corsOptions)
	r.Use(limiter.RateLimit)

	r.Methods("OPTIONS").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	r.PathPrefix("/swagger/").Handler(httpSwagger.WrapHandler)

	apiV1 := v1.NewAPIv1(svc)
	apiV1Router := r.PathPrefix("/api/v1").Subrouter()
	apiV1.RegisterRoutes(apiV1Router)

	log.Printf("Starting server on :%d", cfg.ServerPort)
	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%d", cfg.ServerPort), handlers.CompressHandler(r)))
}
