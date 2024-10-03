package middleware

import (
    "net/http"
    "time"

    "github.com/go-redis/redis/v8"
    "github.com/mcopur/sap-assist/internal/utils"
)

type RateLimiter struct {
    redisClient *redis.Client
    maxRequests int
    duration    time.Duration
}

func NewRateLimiter(redisClient *redis.Client, maxRequests int, duration time.Duration) *RateLimiter {
    return &RateLimiter{
        redisClient: redisClient,
        maxRequests: maxRequests,
        duration:    duration,
    }
}

func (rl *RateLimiter) RateLimit(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        ctx := r.Context()
        key := "rate_limit:" + r.RemoteAddr

        count, err := rl.redisClient.Incr(ctx, key).Result()
        if err != nil {
            utils.RespondWithError(w, http.StatusInternalServerError, "Rate limiting error")
            return
        }

        if count == 1 {
            rl.redisClient.Expire(ctx, key, rl.duration)
        }

        if count > int64(rl.maxRequests) {
            utils.RespondWithError(w, http.StatusTooManyRequests, "Rate limit exceeded")
            return
        }

        next.ServeHTTP(w, r)
    })
}