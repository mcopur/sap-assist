package utils

import (
    "encoding/json"
    "fmt"
    "net/http"
)

type AppError struct {
    Code    int    `json:"code"`
    Message string `json:"message"`
    Err     error  `json:"-"` // Bu alan JSON çıktısında görünmeyecek
}

func (e *AppError) Error() string {
    return fmt.Sprintf("code: %d, message: %s, error: %v", e.Code, e.Message, e.Err)
}

func NewAppError(code int, message string, err error) *AppError {
    return &AppError{
        Code:    code,
        Message: message,
        Err:     err,
    }
}

func RespondWithError(w http.ResponseWriter, appErr *AppError) {
    RespondWithJSON(w, appErr.Code, appErr)
}

func RespondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
    response, _ := json.Marshal(payload)
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(code)
    w.Write(response)
}