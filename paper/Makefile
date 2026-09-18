.PHONY: all data check clean

all:
	pdflatex -interaction=nonstopmode -halt-on-error main.tex
	bibtex main
	pdflatex -interaction=nonstopmode -halt-on-error main.tex
	pdflatex -interaction=nonstopmode -halt-on-error main.tex

data:
	python3 scripts/build_data.py
	python3 scripts/build_comparisons.py
	python3 scripts/build_visuals.py
	python3 scripts/build_field_comparison.py
	python3 scripts/build_review_analysis.py
	python3 scripts/review_loss_control.py evaluate

check:
	python3 scripts/verify_paper.py

clean:
	rm -f main.aux main.bbl main.blg main.log main.out
