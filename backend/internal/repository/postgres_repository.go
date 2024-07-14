package repository

import (
    "context"
    "fmt"

    "github.com/jackc/pgx/v4/pgxpool"
    "github.com/mcopur/sap-assist/internal/models"
    "github.com/mcopur/sap-assist/internal/utils"
)

type PostgresRepository struct {
    db *pgxpool.Pool
}

func NewPostgresRepository(db *pgxpool.Pool) *PostgresRepository {
    return &PostgresRepository{db: db}
}

// User Repository Methods

func (r *PostgresRepository) CreateUser(user *models.User) error {
    encryptedPassword, err := utils.Encrypt(user.PasswordHash)
    if err != nil {
        utils.ErrorLogger.Printf("Error encrypting password: %v", err)
        return fmt.Errorf("error encrypting password: %w", err)
    }

    query := `INSERT INTO users (username, email, password_hash, first_name, last_name, role) 
              VALUES ($1, $2, $3, $4, $5, $6) RETURNING id, created_at, updated_at`
    
    err = r.db.QueryRow(context.Background(), query, 
        user.Username, user.Email, encryptedPassword, user.FirstName, user.LastName, user.Role).
        Scan(&user.ID, &user.CreatedAt, &user.UpdatedAt)
    
    if err != nil {
        utils.ErrorLogger.Printf("Error creating user: %v", err)
        return fmt.Errorf("error creating user: %w", err)
    }
    return nil
}

func (r *PostgresRepository) GetUserByID(id int) (*models.User, error) {
    query := `SELECT id, username, email, password_hash, first_name, last_name, role, created_at, updated_at 
              FROM users WHERE id = $1`
    
    user := &models.User{}
    err := r.db.QueryRow(context.Background(), query, id).Scan(
        &user.ID, &user.Username, &user.Email, &user.PasswordHash, &user.FirstName, 
        &user.LastName, &user.Role, &user.CreatedAt, &user.UpdatedAt,
    )
    
    if err != nil {
        utils.ErrorLogger.Printf("Error getting user by ID %d: %v", id, err)
        return nil, fmt.Errorf("error getting user: %w", err)
    }

    decryptedPassword, err := utils.Decrypt(user.PasswordHash)
    if err != nil {
        utils.ErrorLogger.Printf("Error decrypting password for user %d: %v", id, err)
        return nil, fmt.Errorf("error decrypting password: %w", err)
    }
    user.PasswordHash = decryptedPassword

    return user, nil
}

func (r *PostgresRepository) UpdateUser(user *models.User) error {
    encryptedPassword, err := utils.Encrypt(user.PasswordHash)
    if err != nil {
        utils.ErrorLogger.Printf("Error encrypting password: %v", err)
        return fmt.Errorf("error encrypting password: %w", err)
    }

    query := `UPDATE users SET username = $1, email = $2, password_hash = $3, first_name = $4, 
              last_name = $5, role = $6, updated_at = CURRENT_TIMESTAMP 
              WHERE id = $7 RETURNING updated_at`
    
    err = r.db.QueryRow(context.Background(), query, 
        user.Username, user.Email, encryptedPassword, user.FirstName, user.LastName, user.Role, user.ID).
        Scan(&user.UpdatedAt)
    
    if err != nil {
        utils.ErrorLogger.Printf("Error updating user %d: %v", user.ID, err)
        return fmt.Errorf("error updating user: %w", err)
    }
    return nil
}

func (r *PostgresRepository) DeleteUser(id int) error {
    query := `DELETE FROM users WHERE id = $1`
    
    _, err := r.db.Exec(context.Background(), query, id)
    if err != nil {
        utils.ErrorLogger.Printf("Error deleting user %d: %v", id, err)
        return fmt.Errorf("error deleting user: %w", err)
    }
    return nil
}

// Leave Request Repository Methods

func (r *PostgresRepository) CreateLeaveRequest(request *models.LeaveRequest) error {
    query := `INSERT INTO leave_requests (user_id, start_date, end_date, leave_type, status, reason) 
              VALUES ($1, $2, $3, $4, $5, $6) RETURNING id, created_at, updated_at`
    
    err := r.db.QueryRow(context.Background(), query, 
        request.UserID, request.StartDate, request.EndDate, request.LeaveType, request.Status, request.Reason).
        Scan(&request.ID, &request.CreatedAt, &request.UpdatedAt)
    
    if err != nil {
        utils.ErrorLogger.Printf("Error creating leave request: %v", err)
        return fmt.Errorf("error creating leave request: %w", err)
    }
    return nil
}

func (r *PostgresRepository) GetLeaveRequestByID(id int) (*models.LeaveRequest, error) {
    query := `SELECT id, user_id, start_date, end_date, leave_type, status, reason, created_at, updated_at 
              FROM leave_requests WHERE id = $1`
    
    request := &models.LeaveRequest{}
    err := r.db.QueryRow(context.Background(), query, id).Scan(
        &request.ID, &request.UserID, &request.StartDate, &request.EndDate, &request.LeaveType, 
        &request.Status, &request.Reason, &request.CreatedAt, &request.UpdatedAt,
    )
    
    if err != nil {
        utils.ErrorLogger.Printf("Error getting leave request by ID %d: %v", id, err)
        return nil, fmt.Errorf("error getting leave request: %w", err)
    }
    return request, nil
}

func (r *PostgresRepository) GetLeaveRequestsByUserIDWithPagination(userID, offset, limit int) ([]*models.LeaveRequest, error) {
    query := `SELECT id, user_id, start_date, end_date, leave_type, status, reason, created_at, updated_at 
              FROM leave_requests 
              WHERE user_id = $1 
              ORDER BY created_at DESC 
              LIMIT $2 OFFSET $3`
    
    rows, err := r.db.Query(context.Background(), query, userID, limit, offset)
    if err != nil {
        utils.ErrorLogger.Printf("Error getting leave requests for user %d: %v", userID, err)
        return nil, fmt.Errorf("error getting leave requests: %w", err)
    }
    defer rows.Close()

    var requests []*models.LeaveRequest
    for rows.Next() {
        request := &models.LeaveRequest{}
        err := rows.Scan(
            &request.ID, &request.UserID, &request.StartDate, &request.EndDate, 
            &request.LeaveType, &request.Status, &request.Reason, 
            &request.CreatedAt, &request.UpdatedAt,
        )
        if err != nil {
            utils.ErrorLogger.Printf("Error scanning leave request: %v", err)
            return nil, fmt.Errorf("error scanning leave request: %w", err)
        }
        requests = append(requests, request)
    }

    if err = rows.Err(); err != nil {
        utils.ErrorLogger.Printf("Error iterating leave requests: %v", err)
        return nil, fmt.Errorf("error iterating leave requests: %w", err)
    }

    return requests, nil
}

func (r *PostgresRepository) UpdateLeaveRequest(request *models.LeaveRequest) error {
    query := `UPDATE leave_requests SET start_date = $1, end_date = $2, leave_type = $3, 
              status = $4, reason = $5, updated_at = CURRENT_TIMESTAMP 
              WHERE id = $6 RETURNING updated_at`
    
    err := r.db.QueryRow(context.Background(), query, 
        request.StartDate, request.EndDate, request.LeaveType, request.Status, request.Reason, request.ID).
        Scan(&request.UpdatedAt)
    
    if err != nil {
        utils.ErrorLogger.Printf("Error updating leave request %d: %v", request.ID, err)
        return fmt.Errorf("error updating leave request: %w", err)
    }
    return nil
}

func (r *PostgresRepository) DeleteLeaveRequest(id int) error {
    query := `DELETE FROM leave_requests WHERE id = $1`
    
    _, err := r.db.Exec(context.Background(), query, id)
    if err != nil {
        utils.ErrorLogger.Printf("Error deleting leave request %d: %v", id, err)
        return fmt.Errorf("error deleting leave request: %w", err)
    }
    return nil
}

// Purchase Request Repository Methods

func (r *PostgresRepository) CreatePurchaseRequest(request *models.PurchaseRequest) error {
    query := `INSERT INTO purchase_requests (user_id, item_name, quantity, estimated_cost, status, reason) 
              VALUES ($1, $2, $3, $4, $5, $6) RETURNING id, created_at, updated_at`
    
    err := r.db.QueryRow(context.Background(), query, 
        request.UserID, request.ItemName, request.Quantity, request.EstimatedCost, request.Status, request.Reason).
        Scan(&request.ID, &request.CreatedAt, &request.UpdatedAt)
    
    if err != nil {
        utils.ErrorLogger.Printf("Error creating purchase request: %v", err)
        return fmt.Errorf("error creating purchase request: %w", err)
    }
    return nil
}

func (r *PostgresRepository) GetPurchaseRequestByID(id int) (*models.PurchaseRequest, error) {
    query := `SELECT id, user_id, item_name, quantity, estimated_cost, status, reason, created_at, updated_at 
              FROM purchase_requests WHERE id = $1`
    
    request := &models.PurchaseRequest{}
    err := r.db.QueryRow(context.Background(), query, id).Scan(
        &request.ID, &request.UserID, &request.ItemName, &request.Quantity, &request.EstimatedCost,
        &request.Status, &request.Reason, &request.CreatedAt, &request.UpdatedAt,
    )
    
    if err != nil {
        utils.ErrorLogger.Printf("Error getting purchase request by ID %d: %v", id, err)
        return nil, fmt.Errorf("error getting purchase request: %w", err)
    }
    return request, nil
}

func (r *PostgresRepository) GetPurchaseRequestsByUserIDWithPagination(userID, offset, limit int) ([]*models.PurchaseRequest, error) {
    query := `SELECT id, user_id, item_name, quantity, estimated_cost, status, reason, created_at, updated_at 
              FROM purchase_requests 
              WHERE user_id = $1 
              ORDER BY created_at DESC 
              LIMIT $2 OFFSET $3`
    
    rows, err := r.db.Query(context.Background(), query, userID, limit, offset)
    if err != nil {
        utils.ErrorLogger.Printf("Error getting purchase requests for user %d: %v", userID, err)
        return nil, fmt.Errorf("error getting purchase requests: %w", err)
    }
    defer rows.Close()

    var requests []*models.PurchaseRequest
    for rows.Next() {
        request := &models.PurchaseRequest{}
        err := rows.Scan(
            &request.ID, &request.UserID, &request.ItemName, &request.Quantity, 
            &request.EstimatedCost, &request.Status, &request.Reason, 
            &request.CreatedAt, &request.UpdatedAt,
        )
        if err != nil {
            utils.ErrorLogger.Printf("Error scanning purchase request: %v", err)
            return nil, fmt.Errorf("error scanning purchase request: %w", err)
        }
        requests = append(requests, request)
    }

    if err = rows.Err(); err != nil {
        utils.ErrorLogger.Printf("Error iterating purchase requests: %v", err)
        return nil, fmt.Errorf("error iterating purchase requests: %w", err)
    }

    return requests, nil
}

func (r *PostgresRepository) UpdatePurchaseRequest(request *models.PurchaseRequest) error {
    query := `UPDATE purchase_requests SET item_name = $1, quantity = $2, estimated_cost = $3, 
              status = $4, reason = $5, updated_at = CURRENT_TIMESTAMP 
              WHERE id = $6 RETURNING updated_at`
    
    err := r.db.QueryRow(context.Background(), query, 
        request.ItemName, request.Quantity, request.EstimatedCost, request.Status, request.Reason, request.ID).
        Scan(&request.UpdatedAt)
    
    if err != nil {
        utils.ErrorLogger.Printf("Error updating purchase request %d: %v", request.ID, err)
        return fmt.Errorf("error updating purchase request: %w", err)
    }
    return nil
}

func (r *PostgresRepository) DeletePurchaseRequest(id int) error {
    query := `DELETE FROM purchase_requests WHERE id = $1`
    
    _, err := r.db.Exec(context.Background(), query, id)
    if err != nil {
        utils.ErrorLogger.Printf("Error deleting purchase request %d: %v", id, err)
        return fmt.Errorf("error deleting purchase request: %w", err)
    }
    return nil
}