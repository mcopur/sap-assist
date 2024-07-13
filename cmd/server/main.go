// @title SAP Assist API
// @version 1.0
// @description This is the API for SAP Assist application
// @host localhost:8080
// @BasePath /
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/mcopur/sap-assist/internal/config"
	"github.com/mcopur/sap-assist/internal/database"
	"github.com/mcopur/sap-assist/internal/middleware"
	"github.com/mcopur/sap-assist/internal/models"
	"github.com/mcopur/sap-assist/internal/service"
	"github.com/mcopur/sap-assist/internal/utils"

	httpSwagger "github.com/swaggo/http-swagger"
	_ "github.com/mcopur/sap-assist/api/docs"
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

	// Swagger documentation
	http.HandleFunc("/swagger/*", httpSwagger.WrapHandler)

	// @Summary Health check endpoint
	// @Description Get the health status of the server
	// @Produce json
	// @Success 200 {object} map[string]string
	// @Router /health [get]
	http.HandleFunc("/health", middleware.Logging(middleware.CORS(func(w http.ResponseWriter, r *http.Request) {
		utils.InfoLogger.Println("Health check requested")
		utils.RespondWithJSON(w, http.StatusOK, map[string]string{"status": "OK"})
	})))

	// @Summary Create a new user
	// @Description Create a new user with the input payload
	// @Accept json
	// @Produce json
	// @Param user body models.User true "Create user"
	// @Success 201 {object} models.User
	// @Failure 400 {object} utils.AppError "Bad Request"
	// @Failure 401 {object} utils.AppError "Unauthorized"
	// @Failure 500 {object} utils.AppError "Internal Server Error"
	// @Router /users [post]
	http.HandleFunc("/users", middleware.Logging(middleware.CORS(middleware.BasicAuth(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			utils.RespondWithError(w, utils.NewAppError(http.StatusMethodNotAllowed, "Method not allowed", nil))
			return
		}

		var user models.User
		if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
			utils.RespondWithError(w, utils.NewAppError(http.StatusBadRequest, "Invalid request payload", err))
			return
		}

		if err := user.Validate(); err != nil {
			utils.RespondWithError(w, utils.NewAppError(http.StatusBadRequest, "Validation error", err))
			return
		}

		if err := svc.CreateUser(&user); err != nil {
			utils.RespondWithError(w, utils.NewAppError(http.StatusInternalServerError, "Failed to create user", err))
			return
		}

		utils.RespondWithJSON(w, http.StatusCreated, user)
	}))))

	// @Summary Create a new leave request
	// @Description Create a new leave request with the input payload
	// @Accept json
	// @Produce json
	// @Param request body models.LeaveRequest true "Create leave request"
	// @Success 201 {object} models.LeaveRequest
	// @Failure 400 {object} utils.AppError "Bad Request"
	// @Failure 401 {object} utils.AppError "Unauthorized"
	// @Failure 500 {object} utils.AppError "Internal Server Error"
	// @Router /leave-requests [post]
	http.HandleFunc("/leave-requests", middleware.Logging(middleware.CORS(middleware.BasicAuth(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			utils.RespondWithError(w, utils.NewAppError(http.StatusMethodNotAllowed, "Method not allowed", nil))
			return
		}

		var request models.LeaveRequest
		if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
			utils.RespondWithError(w, utils.NewAppError(http.StatusBadRequest, "Invalid request payload", err))
			return
		}

		if err := request.Validate(); err != nil {
			utils.RespondWithError(w, utils.NewAppError(http.StatusBadRequest, "Validation error", err))
			return
		}

		if err := svc.CreateLeaveRequest(&request); err != nil {
			utils.RespondWithError(w, utils.NewAppError(http.StatusInternalServerError, "Failed to create leave request", err))
			return
		}

		utils.RespondWithJSON(w, http.StatusCreated, request)
	}))))

	// @Summary Create a new purchase request
	// @Description Create a new purchase request with the input payload
	// @Accept json
	// @Produce json
	// @Param request body models.PurchaseRequest true "Create purchase request"
	// @Success 201 {object} models.PurchaseRequest
	// @Failure 400 {object} utils.AppError "Bad Request"
	// @Failure 401 {object} utils.AppError "Unauthorized"
	// @Failure 500 {object} utils.AppError "Internal Server Error"
	// @Router /purchase-requests [post]
	http.HandleFunc("/purchase-requests", middleware.Logging(middleware.CORS(middleware.BasicAuth(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			utils.RespondWithError(w, utils.NewAppError(http.StatusMethodNotAllowed, "Method not allowed", nil))
			return
		}

		var request models.PurchaseRequest
		if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
			utils.RespondWithError(w, utils.NewAppError(http.StatusBadRequest, "Invalid request payload", err))
			return
		}

		if err := request.Validate(); err != nil {
			utils.RespondWithError(w, utils.NewAppError(http.StatusBadRequest, "Validation error", err))
			return
		}

		if err := svc.CreatePurchaseRequest(&request); err != nil {
			utils.RespondWithError(w, utils.NewAppError(http.StatusInternalServerError, "Failed to create purchase request", err))
			return
		}

		utils.RespondWithJSON(w, http.StatusCreated, request)
	}))))

	// Combined handler for leave requests and purchase requests
	http.HandleFunc("/users/", middleware.Logging(middleware.CORS(middleware.BasicAuth(func(w http.ResponseWriter, r *http.Request) {
		if strings.HasSuffix(r.URL.Path, "/leave-requests") {
			if r.Method == http.MethodGet {
				handleGetLeaveRequests(w, r, svc)
			} else {
				utils.RespondWithError(w, utils.NewAppError(http.StatusMethodNotAllowed, "Method not allowed", nil))
			}
		} else if strings.HasSuffix(r.URL.Path, "/purchase-requests") {
			if r.Method == http.MethodGet {
				handleGetPurchaseRequests(w, r, svc)
			} else {
				utils.RespondWithError(w, utils.NewAppError(http.StatusMethodNotAllowed, "Method not allowed", nil))
			}
		} else {
			utils.RespondWithError(w, utils.NewAppError(http.StatusNotFound, "Not found", nil))
		}
	}))))

	utils.InfoLogger.Printf("Starting server on :%d", cfg.ServerPort)
	if err := http.ListenAndServe(fmt.Sprintf(":%d", cfg.ServerPort), nil); err != nil {
		utils.ErrorLogger.Fatalf("Error starting server: %v", err)
	}
}

// @Summary Get leave requests for a user
// @Description Get all leave requests for a specific user
// @Produce json
// @Param user_id path int true "User ID"
// @Param page query int false "Page number"
// @Param limit query int false "Number of items per page"
// @Success 200 {array} models.LeaveRequest
// @Failure 400 {object} utils.AppError "Bad Request"
// @Failure 401 {object} utils.AppError "Unauthorized"
// @Failure 500 {object} utils.AppError "Internal Server Error"
// @Router /users/{user_id}/leave-requests [get]
func handleGetLeaveRequests(w http.ResponseWriter, r *http.Request, svc *service.Service) {
	parts := strings.Split(r.URL.Path, "/")
	if len(parts) != 4 {
		utils.RespondWithError(w, utils.NewAppError(http.StatusBadRequest, "Invalid URL", nil))
		return
	}

	userID, err := strconv.Atoi(parts[2])
	if err != nil {
		utils.RespondWithError(w, utils.NewAppError(http.StatusBadRequest, "Invalid user ID", err))
		return
	}

	pagination := &models.PaginationQuery{}
	if err := r.ParseForm(); err == nil {
		if page, err := strconv.Atoi(r.FormValue("page")); err == nil {
			pagination.Page = page
		}
		if limit, err := strconv.Atoi(r.FormValue("limit")); err == nil {
			pagination.Limit = limit
		}
	}

	requests, err := svc.GetLeaveRequestsByUserID(userID, pagination)
	if err != nil {
		utils.RespondWithError(w, utils.NewAppError(http.StatusInternalServerError, "Failed to get leave requests", err))
		return
	}

	utils.RespondWithJSON(w, http.StatusOK, requests)
}

// @Summary Get purchase requests for a user
// @Description Get all purchase requests for a specific user
// @Produce json
// @Param user_id path int true "User ID"
// @Param page query int false "Page number"
// @Param limit query int false "Number of items per page"
// @Success 200 {array} models.PurchaseRequest
// @Failure 400 {object} utils.AppError "Bad Request"
// @Failure 401 {object} utils.AppError "Unauthorized"
// @Failure 500 {object} utils.AppError "Internal Server Error"
// @Router /users/{user_id}/purchase-requests [get]
func handleGetPurchaseRequests(w http.ResponseWriter, r *http.Request, svc *service.Service) {
	parts := strings.Split(r.URL.Path, "/")
	if len(parts) != 4 {
		utils.RespondWithError(w, utils.NewAppError(http.StatusBadRequest, "Invalid URL", nil))
		return
	}

	userID, err := strconv.Atoi(parts[2])
	if err != nil {
		utils.RespondWithError(w, utils.NewAppError(http.StatusBadRequest, "Invalid user ID", err))
		return
	}

	pagination := &models.PaginationQuery{}
	if err := r.ParseForm(); err == nil {
		if page, err := strconv.Atoi(r.FormValue("page")); err == nil {
			pagination.Page = page
		}
		if limit, err := strconv.Atoi(r.FormValue("limit")); err == nil {
			pagination.Limit = limit
		}
	}

	requests, err := svc.GetPurchaseRequestsByUserID(userID, pagination)
	if err != nil {
		utils.RespondWithError(w, utils.NewAppError(http.StatusInternalServerError, "Failed to get purchase requests", err))
		return
	}

	utils.RespondWithJSON(w, http.StatusOK, requests)
}