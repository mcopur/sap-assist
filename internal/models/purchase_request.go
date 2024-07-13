package models

import "time"

type PurchaseRequest struct {
    ID             int       `json:"id"`
    UserID         int       `json:"user_id"`
    ItemName       string    `json:"item_name"`
    Quantity       int       `json:"quantity"`
    EstimatedCost  float64   `json:"estimated_cost"`
    Status         string    `json:"status"`
    Reason         string    `json:"reason"`
    CreatedAt      time.Time `json:"created_at"`
    UpdatedAt      time.Time `json:"updated_at"`
}