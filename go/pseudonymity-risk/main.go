package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"
)

type Check struct {
	Columns                  []string            `json:"columns"`
	Groups                   int                 `json:"groups"`
	MinimumGroupSize         int                 `json:"minimum_group_size"`
	MaximumGroupSize         int                 `json:"maximum_group_size"`
	UniqueGroups             int                 `json:"unique_groups"`
	EstimatedSinglingOutRate float64             `json:"estimated_singling_out_rate"`
	UniqueGroupExamples      []map[string]string `json:"unique_group_examples"`
}

type Report struct {
	Engine string  `json:"engine"`
	Rows   int     `json:"rows"`
	Profile string `json:"profile"`
	Note   string  `json:"note"`
	Checks []Check `json:"checks"`
}

func main() {
	input := flag.String("input", "", "CSV input path")
	setsJSON := flag.String("sets", "[]", "JSON array of quasi-identifier column sets")
	profile := flag.String("profile", "ad-hoc", "Profile name")
	flag.Parse()

	if *input == "" {
		fail("missing --input")
	}

	var sets [][]string
	if err := json.Unmarshal([]byte(*setsJSON), &sets); err != nil {
		fail("invalid --sets JSON: %v", err)
	}

	rows, err := readRows(*input)
	if err != nil {
		fail("%v", err)
	}

	report := Report{
		Engine: "go",
		Rows: len(rows),
		Profile: *profile,
		Note: "k-anonymity here is a screening signal, not a full re-identification risk assessment.",
	}
	for _, columns := range sets {
		report.Checks = append(report.Checks, kAnonymity(rows, columns))
	}

	encoded, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		fail("%v", err)
	}
	fmt.Println(string(encoded))
}

func readRows(path string) ([]map[string]string, error) {
	handle, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer handle.Close()

	reader := csv.NewReader(handle)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}
	if len(records) == 0 {
		return []map[string]string{}, nil
	}

	headers := records[0]
	rows := make([]map[string]string, 0, len(records)-1)
	for _, record := range records[1:] {
		row := map[string]string{}
		for index, header := range headers {
			if index < len(record) {
				row[header] = record[index]
			} else {
				row[header] = ""
			}
		}
		rows = append(rows, row)
	}
	return rows, nil
}

func kAnonymity(rows []map[string]string, columns []string) Check {
	check := Check{Columns: columns}
	if len(rows) == 0 {
		return check
	}

	groups := map[string]int{}
	valuesByKey := map[string][]string{}
	for _, row := range rows {
		values := make([]string, len(columns))
		for index, column := range columns {
			values[index] = row[column]
		}
		key := strings.Join(values, "\x1f")
		groups[key]++
		valuesByKey[key] = values
	}

	minSize := len(rows)
	maxSize := 0
	unique := 0
	examples := []map[string]string{}
	for key, size := range groups {
		if size < minSize {
			minSize = size
		}
		if size > maxSize {
			maxSize = size
		}
		if size == 1 {
			unique++
			if len(examples) < 10 {
				example := map[string]string{}
				for index, column := range columns {
					example[column] = valuesByKey[key][index]
				}
				examples = append(examples, example)
			}
		}
	}

	check.Groups = len(groups)
	check.MinimumGroupSize = minSize
	check.MaximumGroupSize = maxSize
	check.UniqueGroups = unique
	check.EstimatedSinglingOutRate = float64(unique) / float64(len(rows))
	check.UniqueGroupExamples = examples
	return check
}

func fail(format string, args ...interface{}) {
	fmt.Fprintf(os.Stderr, format + "\n", args...)
	os.Exit(1)
}
