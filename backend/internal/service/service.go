package service

import (
	"bytes"
	"encoding/json"
	"net/http"

	"github.com/mcopur/sap-assist/internal/models"
	"github.com/mcopur/sap-assist/internal/repository"
	"github.com/mcopur/sap-assist/internal/utils"
)

type Service struct {
	repo       *repository.PostgresRepository
	NLPService *NLPService
	httpClient *http.Client
}

func NewService(repo *repository.PostgresRepository, nlpService *NLPService) *Service {
	return &Service{
		repo:       repo,
		NLPService: nlpService,
		httpClient: &http.Client{},
	}
}

func (s *Service) SendLeaveRequest(personnelNumber, startDate, endDate string) (interface{}, error) {
	url := "https://10.1.4.21:44300/sap/opu/odata/sap/ZCXP_LEAVE_REQUEST_SRV/LEAVE_REQUESTSet"
	payload := map[string]interface{}{
		"d": map[string]interface{}{
			"PersonnelNumber": personnelNumber,
			"StartDate":       startDate,
			"EndDate":         endDate,
			"RequestId":       "0AA94D873C191EDAA6B96F42599EEB77",
		},
	}
	jsonPayload, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequest("PUT", url, bytes.NewBuffer(jsonPayload))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-CSRF-TOKEN", "FETCH")

	resp, err := s.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return result, nil
}

// User Service Methods
func (s *Service) CreateUser(user *models.User) error {
	utils.InfoLogger.Printf("Creating user: %s", user.Username)
	err := s.repo.CreateUser(user)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to create user: %v", err)
		return utils.NewAppError(500, "Failed to create user", err)
	}
	return nil
}

func (s *Service) GetUserByID(id int) (*models.User, error) {
	utils.InfoLogger.Printf("Getting user by ID: %d", id)
	user, err := s.repo.GetUserByID(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to get user by ID: %v", err)
		return nil, utils.NewAppError(500, "Failed to get user", err)
	}
	return user, nil
}

func (s *Service) UpdateUser(user *models.User) error {
	utils.InfoLogger.Printf("Updating user: %d", user.ID)
	err := s.repo.UpdateUser(user)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to update user: %v", err)
		return utils.NewAppError(500, "Failed to update user", err)
	}
	return nil
}

func (s *Service) DeleteUser(id int) error {
	utils.InfoLogger.Printf("Deleting user: %d", id)
	err := s.repo.DeleteUser(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to delete user: %v", err)
		return utils.NewAppError(500, "Failed to delete user", err)
	}
	return nil
}

// Leave Request Service Methods
func (s *Service) CreateLeaveRequest(request *models.LeaveRequest) error {
	utils.InfoLogger.Printf("Creating leave request for user: %d", request.UserID)
	err := s.repo.CreateLeaveRequest(request)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to create leave request: %v", err)
		return utils.NewAppError(500, "Failed to create leave request", err)
	}
	return nil
}

func (s *Service) GetLeaveRequestByID(id int) (*models.LeaveRequest, error) {
	utils.InfoLogger.Printf("Getting leave request by ID: %d", id)
	request, err := s.repo.GetLeaveRequestByID(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to get leave request by ID: %v", err)
		return nil, utils.NewAppError(500, "Failed to get leave request", err)
	}
	return request, nil
}

func (s *Service) GetLeaveRequestsByUserID(userID int, pagination *models.PaginationQuery) ([]*models.LeaveRequest, error) {
	utils.InfoLogger.Printf("Getting leave requests for user: %d", userID)
	requests, err := s.repo.GetLeaveRequestsByUserIDWithPagination(userID, pagination.GetOffset(), pagination.GetLimit())
	if err != nil {
		utils.ErrorLogger.Printf("Failed to get leave requests for user: %v", err)
		return nil, utils.NewAppError(500, "Failed to get leave requests", err)
	}
	return requests, nil
}

func (s *Service) UpdateLeaveRequest(request *models.LeaveRequest) error {
	utils.InfoLogger.Printf("Updating leave request: %d", request.ID)
	err := s.repo.UpdateLeaveRequest(request)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to update leave request: %v", err)
		return utils.NewAppError(500, "Failed to update leave request", err)
	}
	return nil
}

func (s *Service) DeleteLeaveRequest(id int) error {
	utils.InfoLogger.Printf("Deleting leave request: %d", id)
	err := s.repo.DeleteLeaveRequest(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to delete leave request: %v", err)
		return utils.NewAppError(500, "Failed to delete leave request", err)
	}
	return nil
}

// Purchase Request Service Methods
func (s *Service) CreatePurchaseRequest(request *models.PurchaseRequest) error {
	utils.InfoLogger.Printf("Creating purchase request for user: %d", request.UserID)
	err := s.repo.CreatePurchaseRequest(request)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to create purchase request: %v", err)
		return utils.NewAppError(500, "Failed to create purchase request", err)
	}
	return nil
}

func (s *Service) GetPurchaseRequestByID(id int) (*models.PurchaseRequest, error) {
	utils.InfoLogger.Printf("Getting purchase request by ID: %d", id)
	request, err := s.repo.GetPurchaseRequestByID(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to get purchase request by ID: %v", err)
		return nil, utils.NewAppError(500, "Failed to get purchase request", err)
	}
	return request, nil
}

func (s *Service) GetPurchaseRequestsByUserID(userID int, pagination *models.PaginationQuery) ([]*models.PurchaseRequest, error) {
	utils.InfoLogger.Printf("Getting purchase requests for user: %d", userID)
	requests, err := s.repo.GetPurchaseRequestsByUserIDWithPagination(userID, pagination.GetOffset(), pagination.GetLimit())
	if err != nil {
		utils.ErrorLogger.Printf("Failed to get purchase requests for user: %v", err)
		return nil, utils.NewAppError(500, "Failed to get purchase requests", err)
	}
	return requests, nil
}

func (s *Service) UpdatePurchaseRequest(request *models.PurchaseRequest) error {
	utils.InfoLogger.Printf("Updating purchase request: %d", request.ID)
	err := s.repo.UpdatePurchaseRequest(request)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to update purchase request: %v", err)
		return utils.NewAppError(500, "Failed to update purchase request", err)
	}
	return nil
}

func (s *Service) DeletePurchaseRequest(id int) error {
	utils.InfoLogger.Printf("Deleting purchase request: %d", id)
	err := s.repo.DeletePurchaseRequest(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to delete purchase request: %v", err)
		return utils.NewAppError(500, "Failed to delete purchase request", err)
	}
	return nil
}
