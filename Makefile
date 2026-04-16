.PHONY: test scenarios verify

test:
	python -m pytest

scenarios:
	python -m experimental.scenarios

verify: test scenarios
