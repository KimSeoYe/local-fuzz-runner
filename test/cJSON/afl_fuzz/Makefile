CC?=gcc
LIBS=../cJSON.c 

all: cJSON_example cJSON_example_file

.PHONY: cJSON_example
cJSON_example: cJSON_example.c $(LIBS)
	$(CC) -o $@ cJSON_example.c  $(LIBS)

.PHONY: cJSON_example_file
cJSON_example_file: cJSON_example_file.c $(LIBS)
	$(CC) -o $@ cJSON_example_file.c  $(LIBS)

clean:
	rm -rf cJSON_example cJSON_example_file 