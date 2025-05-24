package main

import (
	"log"
	"os"

	"github.com/Alter-Sitanshu/learning_Go/env"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load(".env")
	os.MkdirAll("./uploads", os.ModePerm)
	if err != nil {
		log.Fatal("Error loading .env", err.Error())
	}

	config := Config{
		addr: env.GetString("PORT", ":8080"),
	}
	app := &Application{
		config: config,
	}

	AppMux := app.mount()
	log.Fatal(app.run(AppMux))
}
