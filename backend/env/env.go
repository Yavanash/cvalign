package env

import (
	"os"
	"strconv"
)

func GetInt(key string, fallback int) int {
	val, ok := os.LookupEnv(key)
	if !ok {
		return fallback
	}
	vali, err := strconv.Atoi(val)
	if err != nil {
		return fallback
	}
	return vali
}

func GetString(key, fallback string) string {
	val, ok := os.LookupEnv(key)
	if !ok {
		return fallback
	}
	return val
}
