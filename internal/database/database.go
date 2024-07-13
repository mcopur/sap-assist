package database

import (
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
	"github.com/mcopur/sap-assist/internal/config"
	"github.com/mcopur/sap-assist/internal/repository"
)

func InitDB(cfg *config.Config) (*sql.DB, error) {
	connStr := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		cfg.DBHost, cfg.DBPort, cfg.DBUser, cfg.DBPassword, cfg.DBName)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	if err = db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return db, nil
}

func NewRepository(db *sql.DB) *repository.PostgresRepository {
	return repository.NewPostgresRepository(db)
}