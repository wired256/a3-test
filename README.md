# Portfolio Template

A starter repo for building and validating a personal portfolio webpage.

![Pipeline Status](your-badge-url-here)

## Structure

```
.
├── index.html                     # Your portfolio page (edit this)
├── style.css                      # Stylesheet (customize this)
├── scripts/
│   └── validate.py                # Checks your portfolio meets requirements
├── .htmlhintrc                    # HTMLHint linting rules
├── .github/
│   └── workflows/
│       └── pipeline.yml          # CI pipeline (you create this in Part 2)
└── README.md
```

## Running the validator locally

```bash
python3 scripts/validate.py
```

The script checks `index.html` against the requirements and prints `[PASS]`
or `[FAIL]` for each.

## CI pipeline

Create `.github/workflows/pipeline.yml` yourself. The file is
intentionally empty. Your pipeline should run `htmlhint` and
`scripts/validate.py` on every push.
