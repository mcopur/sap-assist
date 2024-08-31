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

func (n *NLPService) ProcessMessage(input models.UserInput) (*models.IntentResponse, error) {
	requestBody, err := json.Marshal(input)
	if err != nil {
		return nil, fmt.Errorf("error marshaling request: %v", err)
	}

	resp, err := n.client.Post(n.baseURL+"/process", "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		return nil, fmt.Errorf("error sending request to NLP service: %v", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("NLP service returned non-200 status code: %d, body: %s", resp.StatusCode, string(body))
	}

	var response models.IntentResponse
	if err := json.Unmarshal(body, &response); err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %v", err)
	}

	return &response, nil
}
