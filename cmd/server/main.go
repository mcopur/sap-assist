package main

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/mcopur/sap-assist/internal/config"
	"github.com/mcopur/sap-assist/internal/database"
	"github.com/mcopur/sap-assist/internal/middleware"
	"github.com/mcopur/sap-assist/internal/models"
	"github.com/mcopur/sap-assist/internal/service"
	"github.com/mcopur/sap-assist/internal/utils"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		utils.ErrorLogger.Fatalf("Failed to load config: %v", err)
	}

	db, err := database.InitDB(cfg)
	if err != nil {
		utils.ErrorLogger.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	repo := database.NewRepository(db)
	svc := service.NewService(repo)

	// Health check endpoint
	http.HandleFunc("/health", middleware.Logging(middleware.CORS(func(w http.ResponseWriter, r *http.Request) {
		utils.InfoLogger.Println("Health check requested")
		response := map[string]string{"status": "OK"}
		json.NewEncoder(w).Encode(response)
	})))

	// User creation endpoint
	http.HandleFunc("/users", middleware.Logging(middleware.CORS(middleware.BasicAuth(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var user models.User
		if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
			utils.ErrorLogger.Printf("Failed to decode user: %v", err)
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		if err := svc.CreateUser(&user); err != nil {
			utils.ErrorLogger.Printf("Failed to create user: %v", err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(user)
	}))))

	// TODO: Add more endpoints here for other operations

	utils.InfoLogger.Printf("Starting server on :%d", cfg.ServerPort)
	if err := http.ListenAndServe(fmt.Sprintf(":%d", cfg.ServerPort), nil); err != nil {
		utils.ErrorLogger.Fatalf("Error starting server: %v", err)
	}
}