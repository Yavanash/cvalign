package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
)

type ScoreRequest struct {
	Filename string `json:"filename"`
	JobDesc  string `json:"job_desc"`
}

type FileMetaData struct {
	Name   string     `json:"name"`
	Type   string     `json:"type"`
	Result MLResponse `json:"result"`
}

type MLResponse struct {
	Status     string   `json:"status"`
	Score      float64  `json:"relevance_score"`
	Assessment string   `json:"assessment"`
	Strengths  []string `json:"strengths"`
	Drawbacks  []string `json:"drawbacks"`
	Remarks    []string `json:"recommendations"`
}

func (app *Application) HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Hello, Status OK\n"))
}

func (app *Application) UploadHandler(w http.ResponseWriter, r *http.Request) {
	// File size max 10 MB
	r.ParseMultipartForm(10 << 20)
	ctx := r.Context()

	// Retrieve the file from the posted form-data
	file, handler, err := r.FormFile("pdf")
	jd := r.FormValue("job_desc")
	candidate := Candidate{
		Name: r.FormValue("candidate_name"),
	}

	if err != nil {
		http.Error(w, "Error retrieving the file", http.StatusBadRequest)
		return
	}
	defer file.Close()
	mimeType := handler.Header.Get("Content-Type")
	if mimeType != "application/pdf" {
		http.Error(w, "Only PDF files are allowed", http.StatusBadRequest)
		return
	} else {
		buffer := make([]byte, 512)
		_, err = file.Read(buffer)
		if err != nil {
			http.Error(w, "Unable to read file", http.StatusInternalServerError)
			return
		}

		file.Seek(0, 0) // Resetting the file pointer

		mimeType = http.DetectContentType(buffer)
		if mimeType != "application/pdf" {
			http.Error(w, "Only PDF files are allowed", http.StatusBadRequest)
			return
		}
	}

	fileMeta := FileMetaData{
		Name: handler.Filename,
		Type: mimeType,
	}

	// Create a file on the server
	dst, err := os.Create("./uploads/" + handler.Filename)
	if err != nil {
		log.Println("error")
		http.Error(w, "Unable to create the file", http.StatusInternalServerError)
		return
	}
	defer dst.Close()

	// Copy the uploaded file to the destination file
	_, err = io.Copy(dst, file)
	if err != nil {
		http.Error(w, "Failed to save the file", http.StatusInternalServerError)
		return
	}

	ch := make(chan MLResponse)
	go func(ch chan MLResponse, filepath string) {
		const MLURL string = "http://ml:8000/score"
		reqBody, _ := json.Marshal(ScoreRequest{
			Filename: filepath,
			JobDesc:  jd,
		})
		resp, err := http.Post(MLURL, "application/json", bytes.NewBuffer([]byte(reqBody)))
		if err != nil {
			log.Println("Request error:", err)
			ch <- MLResponse{Status: "error", Score: 0.0}
			return
		}
		defer resp.Body.Close()
		var apiResp MLResponse

		decoder := json.NewDecoder(resp.Body)
		decoder.DisallowUnknownFields()
		err = decoder.Decode(&apiResp)
		if err != nil {
			log.Println("Decode error:", err)
			ch <- MLResponse{Status: "error", Score: 0.0}
			return
		}
		ch <- apiResp
	}(ch, handler.Filename)

	mlresp := <-ch
	fileMeta.Result = mlresp
	candidate.Score = int64(fileMeta.Result.Score)
	app.store.InsertCandidate(ctx, &candidate)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	log.Printf("File uploaded successfully!\n")

	json.NewEncoder(w).Encode(fileMeta)
}

func (app *Application) GetLeaderboardHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	leaderboard, err := app.store.GetLeaderboard(ctx)
	if err != nil {
		jsonResponse(w, http.StatusInternalServerError, "error getting leaderboard")
		return
	}
	jsonResponse(w, http.StatusOK, leaderboard)
}
