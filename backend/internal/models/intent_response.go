// backend/internal/models/intent_response.go
package models

type IntentResponse struct {
	Intent     string              `json:"intent"`
	Confidence float64             `json:"confidence"`
	Response   string              `json:"response"`
	Entities   map[string][]string `json:"entities"`
}
