# Makefile for Multi-sistemas Project

all:
	@echo "Running Full Pipeline..."
	@python automate_pipeline.py all

train:
	@echo "Phase: Training..."
	@python automate_pipeline.py train

evaluate:
	@echo "Phase: Evaluation..."
	@python automate_pipeline.py evaluate

test:
	@echo "Phase: Real Test..."
	@python automate_pipeline.py test

kill:
	@echo "Stopping servers..."
	@python automate_pipeline.py kill

clean:
	@del /Q model.pkl training_history.json *.png
	@echo "Cleaned artifacts."
