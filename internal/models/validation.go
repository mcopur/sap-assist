package models

import (
    "github.com/go-playground/validator/v10"
)

var validate *validator.Validate

func init() {
    validate = validator.New()
}

func (u *User) Validate() error {
    return validate.Struct(u)
}

func (l *LeaveRequest) Validate() error {
    return validate.Struct(l)
}

func (p *PurchaseRequest) Validate() error {
    return validate.Struct(p)
}