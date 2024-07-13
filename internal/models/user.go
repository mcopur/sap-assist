package models

import "time"

type User struct {
    ID           int       `json:"id"`
    Username     string    `json:"username" validate:"required,min=3,max=50"`
    Email        string    `json:"email" validate:"required,email"`
    PasswordHash string    `json:"-" validate:"required"`
    FirstName    string    `json:"first_name" validate:"required"`
    LastName     string    `json:"last_name" validate:"required"`
    Role         string    `json:"role" validate:"required,oneof=admin user"`
    CreatedAt    time.Time `json:"created_at"`
    UpdatedAt    time.Time `json:"updated_at"`
}