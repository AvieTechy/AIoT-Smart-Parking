# Output configuration
OUTPUT_NAME = specs
OUTPUT_DIR = ./release
OUTPUT_PDF = $(OUTPUT_DIR)/$(OUTPUT_NAME).pdf

# Pandoc and template configuration
PANDOC = pandoc
PDF_ENGINE = xelatex
TEMPLATE_FILE = ./title/template.tex

# Find all markdown source files in the content directory
MD_SOURCES = $(sort $(wildcard ./content/*.md))


# Check if there's a metadata files
METADATA_FILE = $(wildcard ./content/metadata.yaml)
METADATA_FLAG = $(if $(METADATA_FILE),--metadata-file=$(METADATA_FILE),)

# Pandoc options
PANDOC_FLAGS = \
	$(METADATA_FLAG) \
	--template=$(TEMPLATE_FILE) \
	--pdf-engine=$(PDF_ENGINE) \
	--table-of-contents \
	--toc-depth=3 \
	--number-sections \
	--highlight-style=tango \
	--variable fontsize=11pt \
	--variable geometry:margin=1in \
	--variable links-as-notes=true \
	--variable colorlinks=true \
	--variable documentclass=report \
	--extract-media=. \
	--resource-path=.:./content:./content/images:./images:../images \
	--from=markdown+implicit_figures+link_attributes+raw_tex \
	--standalone \
	--quiet

# Default target
all: clean $(OUTPUT_PDF)

# Rule to build the PDF
$(OUTPUT_PDF): $(MD_SOURCES) $(TEMPLATE_FILE)
	@mkdir -p $(OUTPUT_DIR)
	@$(PANDOC) $(MD_SOURCES) $(PANDOC_FLAGS) -o $@
	@echo "PDF created: $(OUTPUT_PDF)"

# Phony target for cleaning up
.PHONY: clean all
clean:
	@rm -f $(OUTPUT_PDF)
	@echo "Cleaned up output files"

# Show help
.PHONY: help
help:
	@echo "Makefile for generating reports with Pandoc"
	@echo ""
	@echo "Targets:"
	@echo "  all     - Generate PDF report (default)"
	@echo "  clean   - Remove generated files"
	@echo "  help    - Show this help message"
	@echo ""
	@echo "Files:"
	@echo "  MD Sources: $(MD_SOURCES)"
	@echo "  Template: $(TEMPLATE_FILE)"
	@echo "  Metadata: $(METADATA_FILE)"
	@echo "  Output: $(OUTPUT_PDF)"
	@echo ""
	@echo "Usage: make [target]"
