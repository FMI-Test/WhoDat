package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"github.com/fatih/color"
	"github.com/nwidger/jsoncolor"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"regexp"
	"strings"
)

const BaseUrl = "https://hr-us.gecloud.io"

var apiKey = ""
var client = &http.Client{}

func getRequest(path string) *http.Request {
	req, err := http.NewRequest("GET", BaseUrl+path, nil)
	if err != nil {
		err.Error()
	}
	req.Header.Set("x-api-key", apiKey)
	req.Header.Set("User-Agent", "whodis-go")
	return req
}

func parseResponse(res *http.Response) bool {
	// Read the body
	body, err := ioutil.ReadAll(res.Body)
	if err != nil {
		err.Error()
	}

	// Check if results were found
	if string(body) != "{}" {
		prettyPrint(string(body))
		return true
	}

	return false
}

func prettyPrint(body string) {
	var data interface{}

	// Unmarshal the string
	err := json.Unmarshal([]byte(body), &data)
	if err != nil {
		err.Error()
	}

	// Colorize the output
	s, err := jsoncolor.MarshalIndent(data, "", "  ")
	if err != nil {
		err.Error()
	}

	// Output the result
	fmt.Println(string(s))
}

func getUserBySSO(sso string) bool {
	req := getRequest("/user")
	query := req.URL.Query()
	query.Add("sso", sso)
	req.URL.RawQuery = query.Encode()
	res, _ := client.Do(req)
	return parseResponse(res)
}

func getUserByName(lastName string, firstName string) bool {
	req := getRequest("/user")
	query := req.URL.Query()
	query.Add("firstName", firstName)
	query.Add("lastName", lastName)
	req.URL.RawQuery = query.Encode()
	res, _ := client.Do(req)
	return parseResponse(res)
}

func getUserByEmail(email string) bool {
	req := getRequest("/user")
	query := req.URL.Query()
	query.Add("email", email)
	req.URL.RawQuery = query.Encode()
	res, _ := client.Do(req)
	return parseResponse(res)
}

func getGroupById(groupId string) bool {
	req := getRequest("/idm")
	query := req.URL.Query()
	query.Add("groupId", groupId)
	req.URL.RawQuery = query.Encode()
	res, _ := client.Do(req)
	return parseResponse(res)
}

func getGroupByEmail(email string) bool {
	req := getRequest("/idm")
	query := req.URL.Query()
	query.Add("email", email)
	req.URL.RawQuery = query.Encode()
	res, _ := client.Do(req)
	return parseResponse(res)
}

func getGroupByName(groupName string) bool {
	req := getRequest("/idm")
	query := req.URL.Query()
	query.Add("name", groupName)
	req.URL.RawQuery = query.Encode()
	res, _ := client.Do(req)
	return parseResponse(res)
}

func main() {
	// Build usage
	flag.Usage = func() {
		color.Yellow("WHO DIS")

		color.Blue("\nUser SSO")
		fmt.Println("whodis 222222222")

		color.Blue("\nUser/group email")
		fmt.Println("whodis user.email@ge.com")
		fmt.Println("whodis aws.account-name@ge.com")

		color.Blue("\nGroup name")
		fmt.Println("whodis @CORP test-account")

		color.Blue("\nUser name")
		fmt.Println("whodis Doe, John")
		fmt.Println("whodis Burdell, George")
		os.Exit(0)
	}
	flag.Parse()

	// Build the argument string
	args := strings.Join(os.Args[1:], " ")

	// Check for api key
	apiKey = os.Getenv("HR_US_KEY")
	if apiKey == "" {
		log.Println("HR_US_KEY environment variable is not configured")
		os.Exit(1)
	}

	// Search for user by SSO
	exp, err := regexp.MatchString("^\\d{9}$", args)
	if err != nil {
		err.Error()
	} else if exp {
		if getUserBySSO(args) {
			return
		}
	}

	// Search for user/group by email
	exp, err = regexp.MatchString("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,4}$", args)
	if err != nil {
		err.Error()
	} else if exp {
		if getUserByEmail(args) {
			return
		} else if getGroupByEmail(args) {
			return
		}
	}

	// Search by IDM group id
	exp, err = regexp.MatchString("^g[0-9]{8}$", args)
	if err != nil {
		err.Error()
	} else if exp {
		if getGroupById(args) {
			return
		}
	}

	// Search by IDM group name
	exp, err = regexp.MatchString("^@.+$", args)
	if err != nil {
		err.Error()
	} else if exp {
		if getGroupByName(args) {
			return
		}
	}

	// Search for user by name
	nameExp := regexp.MustCompile("^([a-zA-Z ]+),\\s?([a-zA-Z]+)$")
	match := nameExp.FindStringSubmatch(args)
	if match != nil {
		if getUserByName(match[1], match[2]) {
			return
		}
	}

	// No results were found
	prettyPrint(`{"error": "No results found"}`)
}
