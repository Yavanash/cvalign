package main

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
)

type FileMetaData struct {
	Name string `json:"name"`
	Size int64  `json:"size"`
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
		Size: handler.Size,
	}

	// Create a file on the server
	dst, err := os.Create("./uploads/" + handler.Filename)
	if err != nil {
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
	w.Header().Set("Content-Type", "apllication/json")
	w.WriteHeader(http.StatusCreated)
	log.Printf("File uploaded successfully!\n")
	json.NewEncoder(w).Encode(fileMeta)
}
