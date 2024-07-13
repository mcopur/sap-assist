package repository

import (
    "database/sql"
    "fmt"
    "github.com/mcopur/sap-assist/internal/models"
)

type PostgresRepository struct {
    db *sql.DB
}

func NewPostgresRepository(db *sql.DB) *PostgresRepository {
    return &PostgresRepository{db: db}
}

// User Repository Implementation
func (r *PostgresRepository) CreateUser(user *models.User) error {
    query := `INSERT INTO users (username, email, password_hash, first_name, last_name, role) 
              VALUES ($1, $2, $3, $4, $5, $6) RETURNING id, created_at, updated_at`
    
    err := r.db.QueryRow(query, user.Username, user.Email, user.PasswordHash, user.FirstName, user.LastName, user.Role).
        Scan(&user.ID, &user.CreatedAt, &user.UpdatedAt)
    
    if err != nil {
        return fmt.Errorf("error creating user: %w", err)
    }
    return nil
}

func (r *PostgresRepository) GetUserByID(id int) (*models.User, error) {
    query := `SELECT id, username, email, password_hash, first_name, last_name, role, created_at, updated_at 
              FROM users WHERE id = $1`
    
    user := &models.User{}
    err := r.db.QueryRow(query, id).Scan(
        &user.ID, &user.Username, &user.Email, &user.PasswordHash, &user.FirstName, 
        &user.LastName, &user.Role, &user.CreatedAt, &user.UpdatedAt,
    )
    
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, fmt.Errorf("user not found")
        }
        return nil, fmt.Errorf("error getting user: %w", err)
    }
    return user, nil
}

func (r *PostgresRepository) UpdateUser(user *models.User) error {
    query := `UPDATE users SET username = $1, email = $2, password_hash = $3, first_name = $4, 
              last_name = $5, role = $6, updated_at = CURRENT_TIMESTAMP 
              WHERE id = $7 RETURNING updated_at`
    
    err := r.db.QueryRow(query, user.Username, user.Email, user.PasswordHash, user.FirstName, 
        user.LastName, user.Role, user.ID).Scan(&user.UpdatedAt)
    
    if err != nil {
        return fmt.Errorf("error updating user: %w", err)
    }
    return nil
}

func (r *PostgresRepository) DeleteUser(id int) error {
    query := `DELETE FROM users WHERE id = $1`
    
    _, err := r.db.Exec(query, id)
    if err != nil {
        return fmt.Errorf("error deleting user: %w", err)
    }
    return nil
}

// Leave Request Repository Implementation
func (r *PostgresRepository) CreateLeaveRequest(request *models.LeaveRequest) error {
    query := `INSERT INTO leave_requests (user_id, start_date, end_date, leave_type, status, reason) 
              VALUES ($1, $2, $3, $4, $5, $6) RETURNING id, created_at, updated_at`
    
    err := r.db.QueryRow(query, request.UserID, request.StartDate, request.EndDate, 
        request.LeaveType, request.Status, request.Reason).
        Scan(&request.ID, &request.CreatedAt, &request.UpdatedAt)
    
    if err != nil {
        return fmt.Errorf("error creating leave request: %w", err)
    }
    return nil
}

func (r *PostgresRepository) GetLeaveRequestByID(id int) (*models.LeaveRequest, error) {
    query := `SELECT id, user_id, start_date, end_date, leave_type, status, reason, created_at, updated_at 
              FROM leave_requests WHERE id = $1`
    
    request := &models.LeaveRequest{}
    err := r.db.QueryRow(query, id).Scan(
        &request.ID, &request.UserID, &request.StartDate, &request.EndDate, &request.LeaveType, 
        &request.Status, &request.Reason, &request.CreatedAt, &request.UpdatedAt,
    )
    
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, fmt.Errorf("leave request not found")
        }
        return nil, fmt.Errorf("error getting leave request: %w", err)
    }
    return request, nil
}

func (r *PostgresRepository) GetLeaveRequestsByUserID(userID int) ([]*models.LeaveRequest, error) {
    query := `SELECT id, user_id, start_date, end_date, leave_type, status, reason, created_at, updated_at 
              FROM leave_requests WHERE user_id = $1`
    
    rows, err := r.db.Query(query, userID)
    if err != nil {
        return nil, fmt.Errorf("error getting leave requests: %w", err)
    }
    defer rows.Close()

    var requests []*models.LeaveRequest
    for rows.Next() {
        request := &models.LeaveRequest{}
        err := rows.Scan(
            &request.ID, &request.UserID, &request.StartDate, &request.EndDate, &request.LeaveType, 
            &request.Status, &request.Reason, &request.CreatedAt, &request.UpdatedAt,
        )
        if err != nil {
            return nil, fmt.Errorf("error scanning leave request: %w", err)
        }
        requests = append(requests, request)
    }
    return requests, nil
}

func (r *PostgresRepository) UpdateLeaveRequest(request *models.LeaveRequest) error {
    query := `UPDATE leave_requests SET start_date = $1, end_date = $2, leave_type = $3, 
              status = $4, reason = $5, updated_at = CURRENT_TIMESTAMP 
              WHERE id = $6 RETURNING updated_at`
    
    err := r.db.QueryRow(query, request.StartDate, request.EndDate, request.LeaveType, 
        request.Status, request.Reason, request.ID).Scan(&request.UpdatedAt)
    
    if err != nil {
        return fmt.Errorf("error updating leave request: %w", err)
    }
    return nil
}

func (r *PostgresRepository) DeleteLeaveRequest(id int) error {
    query := `DELETE FROM leave_requests WHERE id = $1`
    
    _, err := r.db.Exec(query, id)
    if err != nil {
        return fmt.Errorf("error deleting leave request: %w", err)
    }
    return nil
}

// Purchase Request Repository Implementation
func (r *PostgresRepository) CreatePurchaseRequest(request *models.PurchaseRequest) error {
    query := `INSERT INTO purchase_requests (user_id, item_name, quantity, estimated_cost, status, reason) 
              VALUES ($1, $2, $3, $4, $5, $6) RETURNING id, created_at, updated_at`
    
    err := r.db.QueryRow(query, request.UserID, request.ItemName, request.Quantity, 
        request.EstimatedCost, request.Status, request.Reason).
        Scan(&request.ID, &request.CreatedAt, &request.UpdatedAt)
    
    if err != nil {
        return fmt.Errorf("error creating purchase request: %w", err)
    }
    return nil
}

func (r *PostgresRepository) GetPurchaseRequestByID(id int) (*models.PurchaseRequest, error) {
    query := `SELECT id, user_id, item_name, quantity, estimated_cost, status, reason, created_at, updated_at 
              FROM purchase_requests WHERE id = $1`
    
    request := &models.PurchaseRequest{}
    err := r.db.QueryRow(query, id).Scan(
        &request.ID, &request.UserID, &request.ItemName, &request.Quantity, &request.EstimatedCost, 
        &request.Status, &request.Reason, &request.CreatedAt, &request.UpdatedAt,
    )
    
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, fmt.Errorf("purchase request not found")
        }
        return nil, fmt.Errorf("error getting purchase request: %w", err)
    }
    return request, nil
}

func (r *PostgresRepository) GetPurchaseRequestsByUserID(userID int) ([]*models.PurchaseRequest, error) {
    query := `SELECT id, user_id, item_name, quantity, estimated_cost, status, reason, created_at, updated_at 
              FROM purchase_requests WHERE user_id = $1`
    
    rows, err := r.db.Query(query, userID)
    if err != nil {
        return nil, fmt.Errorf("error getting purchase requests: %w", err)
    }
    defer rows.Close()

    var requests []*models.PurchaseRequest
    for rows.Next() {
        request := &models.PurchaseRequest{}
        err := rows.Scan(
            &request.ID, &request.UserID, &request.ItemName, &request.Quantity, &request.EstimatedCost, 
            &request.Status, &request.Reason, &request.CreatedAt, &request.UpdatedAt,
        )
        if err != nil {
            return nil, fmt.Errorf("error scanning purchase request: %w", err)
        }
        requests = append(requests, request)
    }
    return requests, nil
}

func (r *PostgresRepository) UpdatePurchaseRequest(request *models.PurchaseRequest) error {
    query := `UPDATE purchase_requests SET item_name = $1, quantity = $2, estimated_cost = $3, 
              status = $4, reason = $5, updated_at = CURRENT_TIMESTAMP 
              WHERE id = $6 RETURNING updated_at`
    
    err := r.db.QueryRow(query, request.ItemName, request.Quantity, request.EstimatedCost, 
        request.Status, request.Reason, request.ID).Scan(&request.UpdatedAt)
    
    if err != nil {
        return fmt.Errorf("error updating purchase request: %w", err)
    }
    return nil
}

func (r *PostgresRepository) DeletePurchaseRequest(id int) error {
    query := `DELETE FROM purchase_requests WHERE id = $1`
    
    _, err := r.db.Exec(query, id)
    if err != nil {
        return fmt.Errorf("error deleting purchase request: %w", err)
    }
    return nil
}