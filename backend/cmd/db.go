package main

import (
	"context"
	"database/sql"
	"time"

	_ "github.com/lib/pq"
)

func mount(addr string, MaxIdleConns, MaxConns, MaxIdleTime int) (*sql.DB, error) {
	db, err := sql.Open("postgres", addr)
	if err != nil {
		return nil, err
	}
	db.SetConnMaxIdleTime(time.Duration(MaxIdleTime) * time.Minute)
	db.SetMaxIdleConns(MaxIdleConns)
	db.SetMaxOpenConns(MaxConns)

	ctx, cancel := context.WithTimeout(context.Background(), time.Minute*3)
	defer cancel()

	err = db.PingContext(ctx)
	if err != nil {
		return nil, err
	}
	return db, nil

}

type store struct {
	db *sql.DB
}

type Candidate struct {
	Name  string `json:"name"`
	Score int64  `json:"score"`
}

func (s *store) InsertCandidate(ctx context.Context, cand *Candidate) error {
	query := `
		INSERT INTO candidates (name, score)
		VALUES ($1, $2)
	`
	_, err := s.db.ExecContext(ctx, query, cand.Name, cand.Score)
	if err != nil {
		return err
	}
	return nil
}

func (s *store) GetLeaderboard(ctx context.Context) ([]Candidate, error) {
	query := `
		SELECT name, score
		FROM candidates
	`
	rows, err := s.db.QueryContext(ctx, query)
	if err != nil {
		return nil, err
	}
	var output []Candidate
	for rows.Next() {
		var c Candidate
		if err := rows.Scan(&c.Name, &c.Score); err != nil {
			return nil, err
		}
		output = append(output, c)
	}

	return output, nil
}
