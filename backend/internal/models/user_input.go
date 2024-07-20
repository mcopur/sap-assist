// backend/internal/models/user_input.go
package models

type UserInput struct {
    Text      string `json:"text"`
    StartDate string `json:"start_date"`
    EndDate   string `json:"end_date"`
}
