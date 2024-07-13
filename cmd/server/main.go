package main

import (
	"encoding/json"
	"net/http"

	"github.com/mcopur/sap-assist/internal/database"
	"github.com/mcopur/sap-assist/internal/models"
	"github.com/mcopur/sap-assist/internal/service"
	"github.com/mcopur/sap-assist/internal/utils"
)

func main() {
	repo, err := database.NewRepository()
	if err != nil {
		utils.ErrorLogger.Fatalf("Failed to create repository: %v", err)
	}

	svc := service.NewService(repo)

	// Health check endpoint
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		utils.InfoLogger.Println("Health check requested")
		response := map[string]string{"status": "OK"}
		json.NewEncoder(w).Encode(response)
	})

	// User creation endpoint
	http.HandleFunc("/users", func(w http.ResponseWriter, r *http.Request) {
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
	})

	// TODO: Add more endpoints here for other operations

	utils.InfoLogger.Println("Starting server on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		utils.ErrorLogger.Fatalf("Error starting server: %v", err)
	}
}