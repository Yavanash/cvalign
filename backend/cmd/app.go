package main

import (
	"fmt"
	"log"
	"os"

	"github.com/Alter-Sitanshu/learning_Go/env"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load(".env")
	os.MkdirAll("./uploads", os.ModePerm)
	fmt.Println("Directory created")
	if err != nil {
		log.Fatal("Error loading .env", err.Error())
	}

	config := Config{
		addr: env.GetString("PORT", ":8080"),
		db: DBConfig{
			addr:         env.GetString("DB_BIND", "postgres://postgres:seccretpassword@localhost:5432/mydb?sslmode=disable"),
			MaxConns:     10,
			MaxIdleConns: 5,
			MaxIdleTime:  5,
		},
	}
	db, err := mount(
		config.db.addr,
		config.db.MaxConns,
		config.db.MaxIdleConns,
		config.db.MaxIdleTime,
	)
	if err != nil {
		log.Fatal(err)
	}
	app := &Application{
		config: config,
		store: store{
			db: db,
		},
	}

	AppMux := app.mount()
	log.Fatal(app.run(AppMux))
}
