GRAFANA_DIR = infra/grafana
PROVISIONING_TEMPLATE_FILE = $(GRAFANA_DIR)/datasource.template.yml
PROVISIONING_OUTPUT_FILE = $(GRAFANA_DIR)/provisioning/datasource.yml

DB_INIT_DIR = infra/database
DB_INIT_TEMPLATE_FILE = $(DB_INIT_DIR)/init.template.sql
DB_INIT_OUTPUT_FILE = $(DB_INIT_DIR)/init.sql

include .env
export $(shell sed 's/=.*//' .env)

# Задача: Сгенерировать provisioning из шаблона
provisioning: clean_provisioning
	@echo "🔧 Генерация Grafana provisioning файла..."
	envsubst < $(PROVISIONING_TEMPLATE_FILE) > $(PROVISIONING_OUTPUT_FILE)
	@echo "✅ Создан: $(PROVISIONING_OUTPUT_FILE)"

# Задача: Очистка provisioning
clean_provisioning:
	rm -f $(PROVISIONING_OUTPUT_FILE)

# Задача: Сгенерировать init_db из шаблона
init_db: clean_init_db
	@echo "🔧 Генерация Database init файла..."
	envsubst < $(DB_INIT_TEMPLATE_FILE) > $(DB_INIT_OUTPUT_FILE)
	@echo "✅ Создан: $(DB_INIT_OUTPUT_FILE)"

# Задача: Очистка init_db
clean_init_db:
	rm -f $(DB_INIT_OUTPUT_FILE)
