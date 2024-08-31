// backend/internal/models/user_input.go
package models

type UserInput struct {
	Text            string            `json:"text"`
	PersonnelNumber string            `json:"personnel_number"`
	Context         map[string]string `json:"context"`
}
