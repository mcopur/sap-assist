package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"

	"github.com/mcopur/sap-assist/internal/models"
)

type NLPService struct {
	baseURL string
	client  *http.Client
}

func NewNLPService(baseURL string) *NLPService {
	return &NLPService{
		baseURL: baseURL,
		client:  &http.Client{},
	}
}

func (s *NLPService) ProcessMessage(input models.UserInput) (*models.IntentResponse, error) {
	url := fmt.Sprintf("%s/process", s.baseURL)
	requestBody, err := json.Marshal(map[string]string{"text": input.Text})
	if err != nil {
		return nil, fmt.Errorf("error marshaling request: %v", err)
	}

	resp, err := s.client.Post(url, "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		return nil, fmt.Errorf("error sending request to NLP service: %v", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		var errorResponse struct {
			Error   string `json:"error"`
			Details string `json:"details"`
		}
		if err := json.Unmarshal(body, &errorResponse); err == nil {
			return nil, fmt.Errorf("NLP service error: %s, details: %s", errorResponse.Error, errorResponse.Details)
		}
		return nil, fmt.Errorf("NLP service returned non-200 status code: %d, body: %s", resp.StatusCode, string(body))
	}

	var response models.IntentResponse
	if err := json.Unmarshal(body, &response); err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %v", err)
	}

	return &response, nil
}
