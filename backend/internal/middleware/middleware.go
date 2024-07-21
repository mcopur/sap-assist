// backend/internal/middleware/middleware.go
package middleware

import (
    "log"
    "net/http"
    "time"

    "github.com/mcopur/sap-assist/internal/utils"
)

func Logging(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        log.Printf("Started %s %s", r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
        log.Printf("Completed %s %s in %v", r.Method, r.URL.Path, time.Since(start))
    }
}

func BasicAuth(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        username, password, ok := r.BasicAuth()
        if !ok || username != "admin" || password != "password" {
            utils.RespondWithError(w, http.StatusUnauthorized, "Unauthorized")
            return
        }
        next.ServeHTTP(w, r)
    }
}
