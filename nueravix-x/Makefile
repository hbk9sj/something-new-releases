verify:
	bash tools/tests/run_tests.sh
	python3 tools/tests/test_review.py
	python3 -m py_compile tools/buffer.py tools/review.py tools/check_x_draft.py tools/push_image.py
	python3 -c "import json; json.load(open('state/history.json'))"
.PHONY: verify
