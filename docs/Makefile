# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Set the PYTHONPATH to include the src directory
PYTHONPATH    = ../src

# Set STREAMLIT_SECRETS_PATH explicitly for Streamlit
STREAMLIT_SECRETS_PATH = ~/.streamlit/secrets.toml

# Put it first so that "make" without argument is like "make help".
help:
	PYTHONPATH=$(PYTHONPATH) @$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	PYTHONPATH=$(PYTHONPATH) $(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
