package service

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"

	"github.com/google/uuid"
	"github.com/mcopur/sap-assist/internal/models"
	"github.com/mcopur/sap-assist/internal/repository"
	"github.com/mcopur/sap-assist/internal/utils"
)

type Service struct {
	repo       *repository.PostgresRepository
	NLPService *NLPService
	httpClient *http.Client
	sapConfig  *SAPConfig
}

type SAPConfig struct {
	BaseURL      string
	ClientID     string
	ClientSecret string
}

func NewService(repo *repository.PostgresRepository, nlpService *NLPService, sapConfig *SAPConfig) *Service {
	return &Service{
		repo:       repo,
		NLPService: nlpService,
		httpClient: &http.Client{},
		sapConfig:  sapConfig,
	}
}

func (s *Service) SendLeaveRequest(personnelNumber, startDate, endDate string) (interface{}, error) {
	url := fmt.Sprintf("%s/sap/opu/odata/sap/ZCXP_LEAVE_REQUEST_SRV/LEAVE_REQUESTSet", s.sapConfig.BaseURL)
	method := "POST"

	requestID := uuid.New().String()
	payload := map[string]interface{}{
		"PersonnelNumber":       personnelNumber,
		"RequestId":             requestID,
		"Status":                "",
		"StatusText":            "",
		"EndDate":               endDate,
		"StartDate":             startDate,
		"RequestOrAttabs":       "",
		"AttabsHours":           "0.00",
		"AttendanceAbsenceDays": "0.00",
		"CalendarDays":          "1.00",
		"PayrollDays":           "0.00",
		"PayrollHours":          "0.00",
		"SubtypeDescription":    "",
		"Deduction":             "",
		"DeductionTooltip":      "",
	}

	jsonPayload, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("error marshaling JSON: %w", err)
	}

	req, err := http.NewRequest(method, url, bytes.NewBuffer(jsonPayload))
	if err != nil {
		return nil, fmt.Errorf("error creating request: %w", err)
	}

	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", fmt.Sprintf("Basic %s", base64.StdEncoding.EncodeToString([]byte(s.sapConfig.ClientID+":"+s.sapConfig.ClientSecret))))

	resp, err := s.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		return nil, fmt.Errorf("unexpected status code: %d, body: %s", resp.StatusCode, string(body))
	}

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %w", err)
	}

	return result, nil
}

func (s *Service) Login(personnelNumber, password string) (string, error) {
	url := fmt.Sprintf("%s/sap/opu/odata/sap/ZCXP_LEAVE_REQUEST_SRV/LEAVE_REQUESTSet", s.sapConfig.BaseURL)
	method := "GET"

	req, err := http.NewRequest(method, url, nil)
	if err != nil {
		return "", err
	}

	auth := base64.StdEncoding.EncodeToString([]byte(personnelNumber + ":" + password))
	req.Header.Add("Authorization", "Basic "+auth)

	resp, err := s.httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("login failed")
	}

	csrfToken := resp.Header.Get("X-CSRF-Token")
	cookie := resp.Header.Get("Set-Cookie")

	token := fmt.Sprintf("%s:%s:%s:%s", personnelNumber, csrfToken, auth, cookie)
	encodedToken := base64.StdEncoding.EncodeToString([]byte(token))

	return encodedToken, nil
}

// User Service Methods
func (s *Service) CreateUser(user *models.User) error {
	utils.InfoLogger.Printf("Creating user: %s", user.Username)
	err := s.repo.CreateUser(user)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to create user: %v", err)
		return utils.NewAppError(utils.ErrorTypeInternal, "Failed to create user", err)
	}
	return nil
}

func (s *Service) GetUserByID(id int) (*models.User, error) {
	utils.InfoLogger.Printf("Getting user by ID: %d", id)
	user, err := s.repo.GetUserByID(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to get user by ID: %v", err)
		return nil, utils.NewAppError(utils.ErrorTypeInternal, "Failed to get user", err)
	}
	return user, nil
}

func (s *Service) UpdateUser(user *models.User) error {
	utils.InfoLogger.Printf("Updating user: %d", user.ID)
	err := s.repo.UpdateUser(user)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to update user: %v", err)
		return utils.NewAppError(utils.ErrorTypeInternal, "Failed to update user", err)
	}
	return nil
}

func (s *Service) DeleteUser(id int) error {
	utils.InfoLogger.Printf("Deleting user: %d", id)
	err := s.repo.DeleteUser(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to delete user: %v", err)
		return utils.NewAppError(utils.ErrorTypeInternal, "Failed to delete user", err)
	}
	return nil
}

// Leave Request Service Methods
func (s *Service) CreateLeaveRequest(request *models.LeaveRequest) error {
	utils.InfoLogger.Printf("Creating leave request for user: %d", request.UserID)
	err := s.repo.CreateLeaveRequest(request)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to create leave request: %v", err)
		return utils.NewAppError(utils.ErrorTypeInternal, "Failed to create leave request", err)
	}
	return nil
}

func (s *Service) GetLeaveRequestByID(id int) (*models.LeaveRequest, error) {
	utils.InfoLogger.Printf("Getting leave request by ID: %d", id)
	request, err := s.repo.GetLeaveRequestByID(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to get leave request by ID: %v", err)
		return nil, utils.NewAppError(utils.ErrorTypeInternal, "Failed to get leave request", err)
	}
	return request, nil
}

func (s *Service) GetLeaveRequestsByUserID(userID int, pagination *models.PaginationQuery) ([]*models.LeaveRequest, error) {
	utils.InfoLogger.Printf("Getting leave requests for user: %d", userID)
	requests, err := s.repo.GetLeaveRequestsByUserIDWithPagination(userID, pagination.GetOffset(), pagination.GetLimit())
	if err != nil {
		utils.ErrorLogger.Printf("Failed to get leave requests for user: %v", err)
		return nil, utils.NewAppError(utils.ErrorTypeInternal, "Failed to get leave requests", err)
	}
	return requests, nil
}

func (s *Service) UpdateLeaveRequest(request *models.LeaveRequest) error {
	utils.InfoLogger.Printf("Updating leave request: %d", request.ID)
	err := s.repo.UpdateLeaveRequest(request)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to update leave request: %v", err)
		return utils.NewAppError(utils.ErrorTypeInternal, "Failed to update leave request", err)
	}
	return nil
}

func (s *Service) DeleteLeaveRequest(id int) error {
	utils.InfoLogger.Printf("Deleting leave request: %d", id)
	err := s.repo.DeleteLeaveRequest(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to delete leave request: %v", err)
		return utils.NewAppError(utils.ErrorTypeInternal, "Failed to delete leave request", err)
	}
	return nil
}

// Purchase Request Service Methods
func (s *Service) CreatePurchaseRequest(request *models.PurchaseRequest) error {
	utils.InfoLogger.Printf("Creating purchase request for user: %d", request.UserID)
	err := s.repo.CreatePurchaseRequest(request)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to create purchase request: %v", err)
		return utils.NewAppError(utils.ErrorTypeInternal, "Failed to create purchase request", err)
	}
	return nil
}

func (s *Service) GetPurchaseRequestByID(id int) (*models.PurchaseRequest, error) {
	utils.InfoLogger.Printf("Getting purchase request by ID: %d", id)
	request, err := s.repo.GetPurchaseRequestByID(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to get purchase request by ID: %v", err)
		return nil, utils.NewAppError(utils.ErrorTypeInternal, "Failed to get purchase request", err)
	}
	return request, nil
}

func (s *Service) GetPurchaseRequestsByUserID(userID int, pagination *models.PaginationQuery) ([]*models.PurchaseRequest, error) {
	utils.InfoLogger.Printf("Getting purchase requests for user: %d", userID)
	requests, err := s.repo.GetPurchaseRequestsByUserIDWithPagination(userID, pagination.GetOffset(), pagination.GetLimit())
	if err != nil {
		utils.ErrorLogger.Printf("Failed to get purchase requests for user: %v", err)
		return nil, utils.NewAppError(utils.ErrorTypeInternal, "Failed to get purchase requests", err)
	}
	return requests, nil
}

func (s *Service) UpdatePurchaseRequest(request *models.PurchaseRequest) error {
	utils.InfoLogger.Printf("Updating purchase request: %d", request.ID)
	err := s.repo.UpdatePurchaseRequest(request)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to update purchase request: %v", err)
		return utils.NewAppError(utils.ErrorTypeInternal, "Failed to update purchase request", err)
	}
	return nil
}

func (s *Service) DeletePurchaseRequest(id int) error {
	utils.InfoLogger.Printf("Deleting purchase request: %d", id)
	err := s.repo.DeletePurchaseRequest(id)
	if err != nil {
		utils.ErrorLogger.Printf("Failed to delete purchase request: %v", err)
		return utils.NewAppError(utils.ErrorTypeInternal, "Failed to delete purchase request", err)
	}
	return nil
}

func (s *Service) ExtractTokenInfo(token string) (string, string, string, string, error) {
	decodedToken, err := base64.StdEncoding.DecodeString(token)
	if err != nil {
		return "", "", "", "", err
	}

	parts := strings.Split(string(decodedToken), ":")
	if len(parts) != 4 {
		return "", "", "", "", fmt.Errorf("invalid token format")
	}

	return parts[0], parts[1], parts[2], parts[3], nil
}

func (s *Service) ProcessMessage(input models.UserInput) (*models.IntentResponse, error) {
	return s.NLPService.ProcessMessage(input)
}
