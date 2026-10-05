# Evaluating Classifiers: Errors, Metrics, and Thresholds

A combined Slidev lesson for Foundations of Machine Learning. The two earlier presentations remain unchanged.

## Files

- `slides.md`: editable slides, with speaker notes and sources on every slide.
- `slides-export.pdf`: static export; regenerate after editing the slides to include the latest changes.
- `components/MulticlassTable.vue`: three-class wildlife matrix with one-versus-rest labels and precision/recall highlights.
- `components/ThresholdLab.vue`: interactive threshold slider on slide 19.
- `examples/fraud-data.json`: invented score bins shared by the live demo, charts, and Python example.
- `examples/threshold_demo.py`: standalone reproduction of the threshold counts, metrics, costs, ROC-AUC, and average precision.

## Presenting

Run `npm run dev -- --port 3035` from this folder, then open `http://localhost:3035`. Speaker notes are available at `http://localhost:3035/presenter/`. Use the right arrow, space bar, or next control to reveal the next element. Every slide has click reveals, with its title visible from the start. Boxes and table rows appear individually, formulas precede worked calculations, and practice answers appear after the questions. The threshold lab appears as a complete interactive unit. After the final reveal, the next advance moves to the next slide.

The core lesson is slides 1–40. Slides 34–38 extend confusion matrices, precision, recall, and averaging to multiclass classification. Slides 41–46 contain an optional section, four extensions, and references. The live slider is interactive in Slidev; the PDF shows its default threshold of 0.50. Slide 20 records the three operating points for use without the live demo.

Suggested 85-minute pacing:

| Slides | Topic | Minutes |
|---|---|---:|
| 1–7 | Motivation, actions, and the confusion matrix | 10 |
| 8–15 | Accuracy, precision, recall, F1, and practice | 15 |
| 16–20 | Scores, threshold changes, and the live lab | 10 |
| 21–26 | Application costs, capacity, objectives, and validation | 15 |
| 27–32 | FPR, ROC-AUC, and precision-recall curves | 10 |
| 33 | Choosing evaluation evidence | 3 |
| 34–38 | Multiclass matrices, class metrics, and averaging | 12 |
| 39–40 | Python pattern and deployment recommendation | 10 |

For 60 minutes, shorten the discussion of the threshold objectives on slide 25 and demonstrate the Python pattern briefly. For 75 minutes, allow more discussion of competing objectives. Optional extensions can support a later class or student reference.

## Examples and calculations

All numerical scenarios are invented for teaching. The 1,000-transaction validation cohort deliberately contains 100 fraud cases so students can follow the arithmetic. Scores are not calibrated probabilities. Opening and rare-event scenarios use different populations, explicitly identified in the slides and notes.

The three displayed thresholds use the same fixed score distribution. Each displayed threshold represents an interval of equivalent cutoffs because the toy data contain only five distinct scores. The Python example searches all distinct operating points and prints a representative threshold of 0.30 for the same decisions as 0.20 in the low-cost review exercise.

The cost tables compare only the three displayed candidates and assume constant costs for each error type, zero cost for correct decisions, and no extra benefits. They are examples of how a policy objective changes threshold preference, not prescriptions for real fraud systems.

Run the companion example with:

```sh
python3 examples/threshold_demo.py
```

Dependencies: Python, NumPy, and scikit-learn. The script uses validation data throughout. It does not create or evaluate an independent test dataset.

## Build and export

The Slidev setup uses the existing course template at `../../../slidev_template` from this folder.

```sh
npm run build
npm run export -- --output slides-export.pdf --dark
```

If browser discovery fails, specify the local browser:

```sh
npm run export -- --output slides-export.pdf --dark --executable-path '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
```

Technical references are linked in the slide notes and final reference slide. No external images or empirical data are used.

Click animations follow Slidev’s native `v-click` directives with explicit step numbers: https://sli.dev/guide/animations .
