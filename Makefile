# =============================
# Variables
# =============================
DB_FILE := store/vault.db
DOCKER_IMAGE := obsidian-headless
DOCKER_CONTAINER := obsidian-api
API_PORT := 8000

# =============================
# Phony targets
# =============================
.PHONY: start stop clean build_db docker_build docker_run

# -----------------------------
# 1️⃣ Start: build DB, Docker, and leave API running
# -----------------------------
start: build_db docker_build docker_run
	@echo "✅ API is running at http://localhost:$(API_PORT)"
	@echo "You can now run curl, browser requests, or other tests manually."

# -----------------------------
# Build SQLite DB
# -----------------------------
build_db:
	@python scripts/build_sqlite.py
	@echo "✅ SQLite DB built at $(DB_FILE)"

# -----------------------------
# Build Docker image
# -----------------------------
docker_build:
	docker build -t $(DOCKER_IMAGE) .
	@echo "✅ Docker image $(DOCKER_IMAGE) built"

# -----------------------------
# Run Docker container (API)
# -----------------------------
docker_run:
	-docker rm -f $(DOCKER_CONTAINER) || true
	docker run -d \
		--name $(DOCKER_CONTAINER) \
		-p $(API_PORT):8000 \
		-v $(PWD)/vault:/app/vault:ro \
		$(DOCKER_IMAGE)
	@echo "✅ Docker container $(DOCKER_CONTAINER) started"

# -----------------------------
# 2️⃣ Stop & clean
# -----------------------------
stop: 
	-docker rm -f $(DOCKER_CONTAINER) || true
	@echo "✅ Docker container $(DOCKER_CONTAINER) stopped"

clean: stop
	@rm -f $(DB_FILE)
	@echo "🧹 Cleaned SQLite DB and Docker container"
