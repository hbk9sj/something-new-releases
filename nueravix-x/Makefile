verify:
	bash tools/tests/run_tests.sh
	python3 -I -S -B tools/tests/test_review.py
	python3 -I -S -B -c "import ast, sys; [ast.parse(open(f).read(), f) for f in sys.argv[1:]]" tools/buffer.py tools/review.py tools/check_x_draft.py tools/push_image.py
	python3 -I -S -B -c "import json; json.load(open('state/history.json'))"
.PHONY: verify
