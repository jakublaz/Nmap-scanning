IMAGE_NAME=nmap-python
FILE_NAME=nmap-python.tar

# Domyślne zadanie
all: save

# Zadanie budowania
build:
	docker build -t $(IMAGE_NAME) .

# Zadanie zapisu
save: build
	docker save $(IMAGE_NAME):latest -o $(FILE_NAME)
	@echo "✅ Obraz zapisany jako $(FILE_NAME)"

# Czyszczenie (opcjonalnie)
clean:
	rm -f $(FILE_NAME)
