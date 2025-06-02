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
}

type FileMetaData struct {
	Name   string     `json:"name"`
	Type   string     `json:"type"`
	Result MLResponse `json:"result"`
}

type MLResponse struct {
	Status  string  `json:"status"`
	Score   float64 `json:"score"`
	Remarks string  `json:"remarks"`
}

func (app *Application) HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Hello, Status OK\n"))
}

func (app *Application) UploadHandler(w http.ResponseWriter, r *http.Request) {
	// File size max 10 MB
	r.ParseMultipartForm(10 << 20)

	// Retrieve the file from the posted form-data
	file, handler, err := r.FormFile("pdf")
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
		const MLURL string = "http://localhost:8000/score"
		reqBody, _ := json.Marshal(ScoreRequest{Filename: filepath})
		resp, err := http.Post(MLURL, "application/json", bytes.NewBuffer([]byte(reqBody)))
		if err != nil {
			log.Println("Request error:", err)
			ch <- MLResponse{Status: "error", Score: 0.0, Remarks: err.Error()}
			return
		}
		defer resp.Body.Close()
		var apiResp MLResponse

		decoder := json.NewDecoder(resp.Body)
		decoder.DisallowUnknownFields()
		err = decoder.Decode(&apiResp)
		if err != nil {
			log.Println("Decode error:", err)
			ch <- MLResponse{Status: "error", Score: 0.0, Remarks: err.Error()}
			return
		}
		ch <- apiResp
	}(ch, handler.Filename)

	mlresp := <-ch
	fileMeta.Result = mlresp
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	log.Printf("File uploaded successfully!\n")

	json.NewEncoder(w).Encode(fileMeta)
}
