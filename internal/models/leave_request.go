package models

import "time"

type LeaveRequest struct {
    ID        int       `json:"id"`
    UserID    int       `json:"user_id"`
    StartDate time.Time `json:"start_date"`
    EndDate   time.Time `json:"end_date"`
    LeaveType string    `json:"leave_type"`
    Status    string    `json:"status"`
    Reason    string    `json:"reason"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}