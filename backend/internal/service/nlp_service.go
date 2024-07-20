// backend/internal/service/nlp_service.go

package service

import (
	"bytes"
	"encoding/json"
	"net/http"

	"github.com/mcopur/sap-assist/internal/models"
)

type NLPService struct {
	baseURL string
}

func NewNLPService(baseURL string) *NLPService {
	return &NLPService{baseURL: baseURL}
}

func (n *NLPService) ClassifyIntent(text string) (string, float64, string, error) {
	requestBody, err := json.Marshal(map[string]string{"text": text})
	if err != nil {
		return "", 0, "", err
	}

	resp, err := http.Post(n.baseURL+"/classify", "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		return "", 0, "", err
	}
	defer resp.Body.Close()

	var response models.IntentResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return "", 0, "", err
	}

	return response.Intent, response.Confidence, response.Response, nil
}
