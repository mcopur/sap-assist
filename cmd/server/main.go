package main

import (
	"fmt"
	"log"
	"net/http"
)

func main() {
	http.HandleFunc("/", handleRoot)
	http.HandleFunc("/health", handleHealth)

	log.Println("Starting server on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}

func handleRoot(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Welcome to SAP Assist!")
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "OK")
}