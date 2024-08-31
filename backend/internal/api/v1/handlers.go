// backend/internal/api/v1/handlers.go
package v1

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"

	"github.com/gorilla/mux"
	"github.com/mcopur/sap-assist/internal/models"
	"github.com/mcopur/sap-assist/internal/service"
	"github.com/mcopur/sap-assist/internal/utils"
)

type APIv1 struct {
	service *service.Service
}

func NewAPIv1(service *service.Service) *APIv1 {
	return &APIv1{service: service}
}

func (api *APIv1) RegisterRoutes(r *mux.Router) {

	r.HandleFunc("/login", api.loginHandler).Methods("POST")

	r.HandleFunc("/users", api.createUserHandler).Methods("POST")
	r.HandleFunc("/users/{id}", api.getUserHandler).Methods("GET")
	r.HandleFunc("/users/{id}", api.updateUserHandler).Methods("PUT")
	r.HandleFunc("/users/{id}", api.deleteUserHandler).Methods("DELETE")

	r.HandleFunc("/leave-requests", api.createLeaveRequestHandler).Methods("POST")
	r.HandleFunc("/leave-requests/{id}", api.getLeaveRequestHandler).Methods("GET")
	r.HandleFunc("/leave-requests/{id}", api.updateLeaveRequestHandler).Methods("PUT")
	r.HandleFunc("/leave-requests/{id}", api.deleteLeaveRequestHandler).Methods("DELETE")
	r.HandleFunc("/users/{userId}/leave-requests", api.getLeaveRequestsByUserHandler).Methods("GET")

	r.HandleFunc("/purchase-requests", api.createPurchaseRequestHandler).Methods("POST")
	r.HandleFunc("/purchase-requests/{id}", api.getPurchaseRequestHandler).Methods("GET")
	r.HandleFunc("/purchase-requests/{id}", api.updatePurchaseRequestHandler).Methods("PUT")
	r.HandleFunc("/purchase-requests/{id}", api.deletePurchaseRequestHandler).Methods("DELETE")
	r.HandleFunc("/users/{userId}/purchase-requests", api.getPurchaseRequestsByUserHandler).Methods("GET")

	r.HandleFunc("/classify", api.ClassifyIntentHandler).Methods("POST")
}

func (api *APIv1) ClassifyIntentHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("Received classify request")

	var userInput models.UserInput
	if err := json.NewDecoder(r.Body).Decode(&userInput); err != nil {
		log.Printf("Error decoding request body: %v", err)
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}

	log.Printf("User input: %+v", userInput)

	intentResponse, err := api.service.NLPService.ClassifyIntent(userInput.Text)
	if err != nil {
		log.Printf("Error classifying intent: %v", err)
		utils.RespondWithError(w, http.StatusInternalServerError, "Error classifying intent")
		return
	}

	log.Printf("NLP response: %+v", intentResponse)

	utils.RespondWithJSON(w, http.StatusOK, intentResponse)
	log.Printf("Response sent successfully")
}

func (api *APIv1) loginHandler(w http.ResponseWriter, r *http.Request) {
	var loginRequest struct {
		PersonnelNumber string `json:"personnel_number"`
		Password        string `json:"password"`
	}

	if err := json.NewDecoder(r.Body).Decode(&loginRequest); err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}

	// Gerçek login işlemi yerine geçici bir token üret
	// Gerçek ortamda bu kod kaldırılmalıdır.
	if loginRequest.PersonnelNumber == "test" && loginRequest.Password == "test" {
		token := "temporary_test_token"
		utils.RespondWithJSON(w, http.StatusOK, map[string]string{"token": token})
		return
	}

	// Gerçek login işlemi
	token, err := api.service.Login(loginRequest.PersonnelNumber, loginRequest.Password)
	if err != nil {
		utils.RespondWithError(w, http.StatusUnauthorized, "Invalid credentials")
		return
	}

	utils.RespondWithJSON(w, http.StatusOK, map[string]string{"token": token})
}

// @Summary Create a new user
// @Description Create a new user with the input payload
// @Tags users
// @Accept  json
// @Produce  json
// @Param user body models.User true "Create user"
// @Success 201 {object} models.User
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /users [post]
func (api *APIv1) createUserHandler(w http.ResponseWriter, r *http.Request) {
	var user models.User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}
	if err := api.service.CreateUser(&user); err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to create user")
		return
	}
	utils.RespondWithJSON(w, http.StatusCreated, user)
}

// @Summary Get a user by ID
// @Description Get a user by their ID
// @Tags users
// @Accept  json
// @Produce  json
// @Param id path int true "User ID"
// @Success 200 {object} models.User
// @Failure 400 {object} utils.ErrorResponse
// @Failure 404 {object} utils.ErrorResponse
// @Router /users/{id} [get]
func (api *APIv1) getUserHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid user ID")
		return
	}
	user, err := api.service.GetUserByID(id)
	if err != nil {
		utils.RespondWithError(w, http.StatusNotFound, "User not found")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, user)
}

// @Summary Update a user
// @Description Update a user with the input payload
// @Tags users
// @Accept  json
// @Produce  json
// @Param id path int true "User ID"
// @Param user body models.User true "Update user"
// @Success 200 {object} models.User
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /users/{id} [put]
func (api *APIv1) updateUserHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid user ID")
		return
	}
	var user models.User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}
	user.ID = id
	if err := api.service.UpdateUser(&user); err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to update user")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, user)
}

// @Summary Delete a user
// @Description Delete a user by their ID
// @Tags users
// @Accept  json
// @Produce  json
// @Param id path int true "User ID"
// @Success 200 {object} map[string]string
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /users/{id} [delete]
func (api *APIv1) deleteUserHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid user ID")
		return
	}
	if err := api.service.DeleteUser(id); err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to delete user")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, map[string]string{"result": "success"})
}

// @Summary Create a new leave request
// @Description Create a new leave request with the input payload
// @Tags leave-requests
// @Accept  json
// @Produce  json
// @Param request body models.LeaveRequest true "Create leave request"
// @Success 201 {object} models.LeaveRequest
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /leave-requests [post]
func (api *APIv1) createLeaveRequestHandler(w http.ResponseWriter, r *http.Request) {
	var request models.LeaveRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}
	if err := api.service.CreateLeaveRequest(&request); err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to create leave request")
		return
	}
	utils.RespondWithJSON(w, http.StatusCreated, request)
}

// @Summary Get a leave request by ID
// @Description Get a leave request by its ID
// @Tags leave-requests
// @Accept  json
// @Produce  json
// @Param id path int true "Leave Request ID"
// @Success 200 {object} models.LeaveRequest
// @Failure 400 {object} utils.ErrorResponse
// @Failure 404 {object} utils.ErrorResponse
// @Router /leave-requests/{id} [get]
func (api *APIv1) getLeaveRequestHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid leave request ID")
		return
	}
	request, err := api.service.GetLeaveRequestByID(id)
	if err != nil {
		utils.RespondWithError(w, http.StatusNotFound, "Leave request not found")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, request)
}

// @Summary Update a leave request
// @Description Update a leave request with the input payload
// @Tags leave-requests
// @Accept  json
// @Produce  json
// @Param id path int true "Leave Request ID"
// @Param request body models.LeaveRequest true "Update leave request"
// @Success 200 {object} models.LeaveRequest
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /leave-requests/{id} [put]
func (api *APIv1) updateLeaveRequestHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid leave request ID")
		return
	}
	var request models.LeaveRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}
	request.ID = id
	if err := api.service.UpdateLeaveRequest(&request); err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to update leave request")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, request)
}

// @Summary Delete a leave request
// @Description Delete a leave request by its ID
// @Tags leave-requests
// @Accept  json
// @Produce  json
// @Param id path int true "Leave Request ID"
// @Success 200 {object} map[string]string
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /leave-requests/{id} [delete]
func (api *APIv1) deleteLeaveRequestHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid leave request ID")
		return
	}
	if err := api.service.DeleteLeaveRequest(id); err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to delete leave request")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, map[string]string{"result": "success"})
}

// @Summary Get leave requests by user ID
// @Description Get all leave requests for a specific user
// @Tags leave-requests
// @Accept  json
// @Produce  json
// @Param userId path int true "User ID"
// @Param page query int false "Page number"
// @Param limit query int false "Number of items per page"
// @Success 200 {array} models.LeaveRequest
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /users/{userId}/leave-requests [get]
func (api *APIv1) getLeaveRequestsByUserHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	userID, err := strconv.Atoi(vars["userId"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid user ID")
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
	requests, err := api.service.GetLeaveRequestsByUserID(userID, pagination)
	if err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to get leave requests")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, requests)
}

// @Summary Create a new purchase request
// @Description Create a new purchase request with the input payload
// @Tags purchase-requests
// @Accept  json
// @Produce  json
// @Param request body models.PurchaseRequest true "Create purchase request"
// @Success 201 {object} models.PurchaseRequest
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /purchase-requests [post]
func (api *APIv1) createPurchaseRequestHandler(w http.ResponseWriter, r *http.Request) {
	var request models.PurchaseRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}
	if err := api.service.CreatePurchaseRequest(&request); err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to create purchase request")
		return
	}
	utils.RespondWithJSON(w, http.StatusCreated, request)
}

// @Summary Get a purchase request by ID
// @Description Get a purchase request by its ID
// @Tags purchase-requests
// @Accept  json
// @Produce  json
// @Param id path int true "Purchase Request ID"
// @Success 200 {object} models.PurchaseRequest
// @Failure 400 {object} utils.ErrorResponse
// @Failure 404 {object} utils.ErrorResponse
// @Router /purchase-requests/{id} [get]
func (api *APIv1) getPurchaseRequestHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid purchase request ID")
		return
	}
	request, err := api.service.GetPurchaseRequestByID(id)
	if err != nil {
		utils.RespondWithError(w, http.StatusNotFound, "Purchase request not found")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, request)
}

// @Summary Update a purchase request
// @Description Update a purchase request with the input payload
// @Tags purchase-requests
// @Accept  json
// @Produce  json
// @Param id path int true "Purchase Request ID"
// @Param request body models.PurchaseRequest true "Update purchase request"
// @Success 200 {object} models.PurchaseRequest
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /purchase-requests/{id} [put]
func (api *APIv1) updatePurchaseRequestHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid purchase request ID")
		return
	}
	var request models.PurchaseRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}
	request.ID = id
	if err := api.service.UpdatePurchaseRequest(&request); err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to update purchase request")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, request)
}

// @Summary Delete a purchase request
// @Description Delete a purchase request by its ID
// @Tags purchase-requests
// @Accept  json
// @Produce  json
// @Param id path int true "Purchase Request ID"
// @Success 200 {object} map[string]string
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /purchase-requests/{id} [delete]
func (api *APIv1) deletePurchaseRequestHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid purchase request ID")
		return
	}
	if err := api.service.DeletePurchaseRequest(id); err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to delete purchase request")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, map[string]string{"result": "success"})
}

// @Summary Get purchase requests by user ID
// @Description Get all purchase requests for a specific user
// @Tags purchase-requests
// @Accept  json
// @Produce  json
// @Param userId path int true "User ID"
// @Param page query int false "Page number"
// @Param limit query int false "Number of items per page"
// @Success 200 {array} models.PurchaseRequest
// @Failure 400 {object} utils.ErrorResponse
// @Failure 500 {object} utils.ErrorResponse
// @Router /users/{userId}/purchase-requests [get]
func (api *APIv1) getPurchaseRequestsByUserHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	userID, err := strconv.Atoi(vars["userId"])
	if err != nil {
		utils.RespondWithError(w, http.StatusBadRequest, "Invalid user ID")
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
	requests, err := api.service.GetPurchaseRequestsByUserID(userID, pagination)
	if err != nil {
		utils.RespondWithError(w, http.StatusInternalServerError, "Failed to get purchase requests")
		return
	}
	utils.RespondWithJSON(w, http.StatusOK, requests)
}
