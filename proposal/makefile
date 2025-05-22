# Makefile for converting Markdown files to PDF and TEX using pandoc

# Directories
SRC_DIR = ./content
BUILD_DIR = ./build
RELEASE_DIR = ./release

# Source files
MARKDOWN_FILES = $(wildcard $(SRC_DIR)/*.md)
METADATA_FILE = $(SRC_DIR)/metadata.yaml

# Output files
PDF_OUTPUT = $(RELEASE_DIR)/proposal.pdf
TEX_OUTPUT = $(RELEASE_DIR)/proposal.tex

# Make sure that the build is always triggered by marking these targets as phony
.PHONY: all pdf tex clean

# Default target: build PDF
all: pdf

# Build PDF from Markdown files
pdf:
	@mkdir -p $(RELEASE_DIR)
	@echo "Converting Markdown to PDF..."
	pandoc $(METADATA_FILE) $(MARKDOWN_FILES) -o $(PDF_OUTPUT) --pdf-engine=xelatex

# Build TEX from Markdown files
tex:
	@mkdir -p $(RELEASE_DIR)
	@echo "Converting Markdown to TEX..."
	pandoc $(METADATA_FILE) $(MARKDOWN_FILES) -o $(TEX_OUTPUT)

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(PDF_OUTPUT) $(TEX_OUTPUT)
