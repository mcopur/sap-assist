package middleware

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/mcopur/sap-assist/internal/utils"
)

type RedisRateLimiter struct {
	client      *redis.Client
	maxRequests int
	duration    time.Duration
}

func NewRedisRateLimiter(client *redis.Client, maxRequests int, duration time.Duration) *RedisRateLimiter {
	return &RedisRateLimiter{
		client:      client,
		maxRequests: maxRequests,
		duration:    duration,
	}
}

func (r *RedisRateLimiter) Allow(key string) bool {
	ctx := context.Background()
	now := time.Now().UnixNano()

	pipe := r.client.Pipeline()
	pipe.ZRemRangeByScore(ctx, key, "0", fmt.Sprintf("%d", now-(r.duration.Nanoseconds())))
	pipe.ZAdd(ctx, key, &redis.Z{Score: float64(now), Member: now})
	pipe.ZCard(ctx, key)
	pipe.Expire(ctx, key, r.duration)

	cmders, err := pipe.Exec(ctx)
	if err != nil {
		return false
	}

	reqCount := cmders[2].(*redis.IntCmd).Val()
	return reqCount <= int64(r.maxRequests)
}

func RateLimit(limiter *RedisRateLimiter) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if !limiter.Allow(r.RemoteAddr) {
				utils.RespondWithError(w, http.StatusTooManyRequests, "Rate limit exceeded")
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}
