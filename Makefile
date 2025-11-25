# Makefile for Multi-sistemas Project

all:
	@echo "Running Full Pipeline..."
	@python automate_pipeline.py all

train:
	@echo "Phase: Training..."
	@python automate_pipeline.py train

clean:
	@echo "Phase: Cleaning..."
	@python automate_pipeline.py clean

evaluate:
	@echo "Phase: Evaluation..."
	@python automate_pipeline.py evaluate

test:
	@echo "Phase: Real Test..."
	@python automate_pipeline.py test

kill:
	@echo "Stopping servers..."
	@python automate_pipeline.py kill
