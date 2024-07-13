package database

import (
    "context"
    "fmt"
    "log"

    "github.com/jackc/pgx/v4/pgxpool"
    "github.com/mcopur/sap-assist/internal/config"
    "github.com/mcopur/sap-assist/internal/repository"
)

var db *pgxpool.Pool

func InitDB(cfg *config.Config) (*pgxpool.Pool, error) {
    connectionString := fmt.Sprintf("postgresql://%s:%s@%s:%d/%s",
        cfg.DBUser, cfg.DBPassword, cfg.DBHost, cfg.DBPort, cfg.DBName)

    poolConfig, err := pgxpool.ParseConfig(connectionString)
    if err != nil {
        return nil, fmt.Errorf("unable to parse connection string: %v", err)
    }

    // Bağlantı havuzu ayarları
    poolConfig.MaxConns = 10
    poolConfig.MinConns = 2

    db, err = pgxpool.ConnectConfig(context.Background(), poolConfig)
    if err != nil {
        return nil, fmt.Errorf("unable to connect to database: %v", err)
    }

    log.Println("Successfully connected to the database")
    return db, nil
}

func GetDB() *pgxpool.Pool {
    return db
}

func NewRepository(db *pgxpool.Pool) *repository.PostgresRepository {
    return repository.NewPostgresRepository(db)
}