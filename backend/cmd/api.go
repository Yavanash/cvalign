package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

type Application struct {
	config Config
	store  store
}

type Config struct {
	addr string
	db   DBConfig
}

type DBConfig struct {
	addr         string
	MaxConns     int
	MaxIdleConns int
	MaxIdleTime  int
}

func (app *Application) mount() http.Handler {
	router := chi.NewRouter()

	// Middleware
	router.Use(middleware.RequestID)
	router.Use(middleware.RealIP)
	router.Use(middleware.Logger)
	router.Use(middleware.Recoverer)

	// Set a timeout value on the request context (ctx), that will signal
	// through ctx.Done() that the request has timed out and further
	// processing should be stopped.
	router.Use(middleware.Timeout(5 * time.Minute))

	// Routes for the API
	router.Route("/v1", func(r chi.Router) {
		r.Use(app.WithCORS)
		r.Get("/health", app.HealthCheckHandler)
		r.Post("/upload", app.UploadHandler)
		r.Get("/leaderboard", app.GetLeaderboardHandler)
	})

	return router
}

func (app *Application) run(mux http.Handler) error {
	server := &http.Server{
		Addr:         app.config.addr,
		Handler:      mux,
		WriteTimeout: time.Second * 30,
		ReadTimeout:  time.Second * 10,
		IdleTimeout:  time.Minute,
	}

	fmt.Printf("Server listening at http://localhost%s\n", app.config.addr)
	return server.ListenAndServe()
}

func jsonResponse(w http.ResponseWriter, status int, data any) error {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	type Resp struct {
		Data any `json:"data"`
	}
	resp := Resp{
		Data: data,
	}
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		return err
	}
	return nil
}
