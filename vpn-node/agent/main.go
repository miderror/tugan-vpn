package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
	_ "modernc.org/sqlite"
)

var (
	db       *sql.DB
	apiToken string
	client   *http.Client
	baseUrl  string
)

type UserUpdate struct {
	Email     string `json:"email"`
	Expiry    int64  `json:"expiry"`
	Enable    bool   `json:"enable"`
	UUID      string `json:"uuid"`
	InboundId int    `json:"inbound_id"`
}

func main() {
	dbPath := os.Getenv("DB_PATH")
	apiToken = os.Getenv("API_TOKEN")
	baseUrl = fmt.Sprintf("http://127.0.0.1:%s%s", os.Getenv("XUI_PORT"), os.Getenv("XUI_PATH"))

	jar, _ := cookiejar.New(nil)
	client = &http.Client{Jar: jar}

	var err error
	db, err = sql.Open("sqlite", dbPath)
	if err != nil {
		log.Fatal(err)
	}

	loginToXUI()

	r := gin.New()
	r.Use(gin.Recovery())

	auth := func(c *gin.Context) {
		if c.GetHeader("X-Agent-Token") != apiToken {
			c.AbortWithStatus(401)
			return
		}
		c.Next()
	}

	api := r.Group("/api", auth)
	{
		api.GET("/traffic-delta", getTrafficDelta)
		api.POST("/bulk-update", bulkUpdate)
		api.POST("/user-update", singleUpdate)
	}

	log.Println("Agent is ready to fly on :8080")
	r.Run(":8080")
}

func loginToXUI() {
	loginUrl := baseUrl + "/login"
	data := url.Values{}
	data.Set("username", os.Getenv("XUI_LOGIN"))
	data.Set("password", os.Getenv("XUI_PASS"))

	resp, err := client.PostForm(loginUrl, data)
	if err != nil || resp.StatusCode != 200 {
		log.Printf("CRITICAL: 3x-ui login failed: %v", err)
	}
}

func getTrafficDelta(c *gin.Context) {
	tx, _ := db.Begin()
	rows, _ := tx.Query("SELECT email, up, down FROM client_traffics WHERE up > 0 OR down > 0")

	type Stat struct {
		E string `json:"e"`
		T int64  `json:"t"`
	}
	var stats []Stat
	var emails []string

	for rows.Next() {
		var e string
		var u, d int64
		rows.Scan(&e, &u, &d)
		stats = append(stats, Stat{E: e, T: u + d})
		emails = append(emails, "'"+e+"'")
	}

	if len(emails) > 0 {
		query := fmt.Sprintf("UPDATE client_traffics SET up = 0, down = 0 WHERE email IN (%s)", strings.Join(emails, ","))
		tx.Exec(query)
	}
	tx.Commit()
	c.JSON(200, stats)
}

func singleUpdate(c *gin.Context) {
	var u UserUpdate
	if err := c.BindJSON(&u); err != nil {
		c.Status(400)
		return
	}

	apiUrl := fmt.Sprintf("%s/panel/api/inbounds/updateClient/%s", baseUrl, u.UUID)

	clientSettings := map[string]interface{}{
		"id":       u.InboundId,
		"settings": fmt.Sprintf(`{"clients": [{"id": "%s", "email": "%s", "totalGB": 0, "expiryTime": %d, "enable": %t}]}`, u.UUID, u.Email, u.Expiry, u.Enable),
	}

	marshaled, _ := json.Marshal(clientSettings)

	resp, err := client.Post(apiUrl, "application/json", strings.NewReader(string(marshaled)))

	if err != nil || resp.StatusCode != 200 {
		c.Status(500)
		return
	}
	c.Status(200)
}

func bulkUpdate(c *gin.Context) {
	var updates []UserUpdate
	c.BindJSON(&updates)

	tx, _ := db.Begin()
	stmt, _ := tx.Prepare("UPDATE client_traffics SET expiry_time = ?, enable = ? WHERE email = ?")
	for _, u := range updates {
		stmt.Exec(u.Expiry, u.Enable, u.Email)
	}
	tx.Commit()

	client.Post(baseUrl+"/panel/api/server/restartXray", "application/json", nil)
	c.Status(200)
}
