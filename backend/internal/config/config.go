// backend/internal/config/config.go
package config

import (
	"fmt"
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

type Config struct {
	DBHost          string
	DBPort          int
	DBUser          string
	DBPassword      string
	DBName          string
	ServerPort      int
	NLPServiceURL   string
	SAPBaseURL      string
	SAPClientID     string
	SAPClientSecret string
	AllowedOrigin   string
	RedisAddr       string
}

func LoadConfig() (*Config, error) {
	err := godotenv.Load()
	if err != nil {
		return nil, fmt.Errorf("error loading .env file: %w", err)
	}

	config := &Config{
		DBHost:          getEnv("DB_HOST", "localhost"),
		DBPort:          getEnvAsInt("DB_PORT", 5432),
		DBUser:          getEnv("DB_USER", ""),
		DBPassword:      getEnv("DB_PASSWORD", ""),
		DBName:          getEnv("DB_NAME", ""),
		ServerPort:      getEnvAsInt("SERVER_PORT", 8080),
		NLPServiceURL:   getEnv("NLP_SERVICE_URL", "http://localhost:5000"),
		SAPBaseURL:      getEnv("SAP_BASE_URL", ""),
		SAPClientID:     getEnv("SAP_CLIENT_ID", ""),
		SAPClientSecret: getEnv("SAP_CLIENT_SECRET", ""),
		AllowedOrigin:   getEnv("ALLOWED_ORIGIN", "http://localhost:5173"),
		RedisAddr:       getEnv("REDIS_ADDR", "localhost:6379"),
	}

	return config, nil
}

func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

func getEnvAsInt(key string, defaultValue int) int {
	valueStr := getEnv(key, "")
	if value, err := strconv.Atoi(valueStr); err == nil {
		return value
	}
	return defaultValue
}
