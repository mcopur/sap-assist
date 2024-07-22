// backend/internal/service/nlp_service.go
package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"

	"github.com/mcopur/sap-assist/internal/models"
)

type NLPService struct {
	baseURL string
}

func NewNLPService(baseURL string) *NLPService {
	return &NLPService{baseURL: baseURL}
}

func (n *NLPService) ClassifyIntent(text string) (*models.IntentResponse, error) {
	requestBody, err := json.Marshal(map[string]string{"text": text})
	if err != nil {
		return nil, fmt.Errorf("error marshaling request: %v", err)
	}

	log.Printf("Sending request to NLP service: %s", string(requestBody))

	resp, err := http.Post(n.baseURL+"/classify", "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		return nil, fmt.Errorf("error sending request to NLP service: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %v", err)
	}

	log.Printf("Received response from NLP service: %s", string(body))

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("NLP service returned non-200 status code: %d, body: %s", resp.StatusCode, string(body))
	}

	var response models.IntentResponse
	if err := json.Unmarshal(body, &response); err != nil {
		return nil, fmt.Errorf("error unmarshaling response: %v", err)
	}

	return &response, nil
}
