# PlantUML Utilities Makefile

# Render all PlantUML diagrams to SVG (default)
render-diagrams:
	python -m utils.puml.cli render
	@echo "Diagrams saved to docs/diagrams/output"

# Render all PlantUML diagrams to PNG
render-diagrams-png:
	python -m utils.puml.cli render --format=png

# Render a specific PlantUML diagram
render-diagram:
	@echo "Usage: make render-diagram FILE=<file>"
	@if [ "$(FILE)" ]; then \
		python -m utils.puml.cli render --file=$(FILE); \
	fi

# Open the PlantUML HTML viewer
view-diagrams:
	# Open the HTML file directly instead of using the CLI
	start docs/diagrams/output/index.html 2>/dev/null || \
	open docs/diagrams/output/index.html 2>/dev/null || \
	xdg-open docs/diagrams/output/index.html 2>/dev/null || \
	echo "Could not open the HTML viewer automatically. Please open docs/diagrams/output/index.html manually."

# Show help
help:
	@echo "PlantUML Utilities Makefile"
	@echo ""
	@echo "Commands:"
	@echo "  make render-diagrams       - Render all PlantUML diagrams to SVG"
	@echo "  make render-diagrams-png   - Render all PlantUML diagrams to PNG"
	@echo "  make render-diagram FILE=<file> - Render a specific PlantUML diagram"
	@echo "  make view-diagrams         - Open the PlantUML HTML viewer"
	@echo "  make help                  - Show this help message"
	@echo ""
	@echo "Example:"
	@echo "  make render-diagram FILE=classifier/classifier_model_diagram.puml"

.PHONY: render-diagrams render-diagrams-png render-diagram view-diagrams help