package config

import (
	"os"
	"strconv"
)

type Config struct {
	ServerPort int
}

func Load() *Config {
	return &Config{
		ServerPort: getEnvAsInt("SERVER_PORT", 8080),
	}
}

func getEnvAsInt(name string, defaultVal int) int {
	valStr := os.Getenv(name)
	if value, err := strconv.Atoi(valStr); err == nil {
		return value
	}
	return defaultVal
}