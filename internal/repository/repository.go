package repository

import "github.com/mcopur/sap-assist/internal/models"

type UserRepository interface {
    Create(user *models.User) error
    GetByID(id int) (*models.User, error)
    Update(user *models.User) error
    Delete(id int) error
}

type LeaveRequestRepository interface {
    Create(request *models.LeaveRequest) error
    GetByID(id int) (*models.LeaveRequest, error)
    GetByUserID(userID int) ([]*models.LeaveRequest, error)
    Update(request *models.LeaveRequest) error
    Delete(id int) error
}

type PurchaseRequestRepository interface {
    Create(request *models.PurchaseRequest) error
    GetByID(id int) (*models.PurchaseRequest, error)
    GetByUserID(userID int) ([]*models.PurchaseRequest, error)
    Update(request *models.PurchaseRequest) error
    Delete(id int) error
}