# BioSignal Studio - Heart Rate & ECG Decision Helper

BioSignal Studio is a Track C (Simulation / Decision-Support) mini-tool for BME 3053C. The Streamlit app models how heart rate and a synthetic ECG-like waveform respond to user-controlled physiological and signal-processing parameters. It is intentionally simple, transparent, and ready for classroom demos.

## Biomedical Context

Cardiovascular biosignals such as heart rate (beats per minute) and the electrocardiogram (ECG) are foundational in biomedical engineering. This tool helps students explore:

- How stress/exercise can change heart-rate trajectories.
- How noise and baseline wander distort ECG recordings.
- How basic bandpass filtering rescues morphology.
- How simple classification buckets (bradycardia / normal / tachycardia) are derived.

The model is educational only - it does **not** predict clinical outcomes.

## Features

- Interactive sidebar controls for HR targets, stress level, duration, sampling rate, noise, baseline drift, and filtering.
- Synthetic ECG generator using Gaussian P-QRS-T templates aligned with the modeled heart rate.
- Optional Butterworth bandpass filter to demonstrate signal cleaning.
- Heart-rate metrics (mean/min/max/std), categorical classification, and narrative interpretation text.
- Clear explanatory copy, expanders, and disclaimers suitable for lab reports or presentations.

## Quick Start

Prerequisites: Python 3.10+ with `pip`.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit automatically serves the dashboard at the URL printed in the terminal.

## Usage Guide

1. **Set parameters** – Use the sidebar sliders to select resting HR, peak/exercise HR, stress level, simulation duration, sampling rate, and noise/baseline amplitudes.
2. **Toggle filtering** – Enable the bandpass filter to adjust low/high cutoffs and order; compare raw versus filtered traces in the "Signals" tab.
3. **Interpret outputs** – Switch to "Summary & Interpretation" to inspect the metrics, HR classification, and educational commentary. Remember: this is a toy model, not medical advice.

Streamlit reruns automatically whenever you change a control; the "Run Simulation" button is provided for clarity.

## Simulation Details

- **Time base:** 5-30 s duration at 200-400 Hz sampling (default 300 Hz).
- **Heart-rate model:** Exponential approach from resting HR toward a stress-weighted peak.
- **ECG synthesis:** Sum of Gaussian P/QRS/T components in phase space, plus user-defined white noise and low-frequency baseline wander.
- **Filtering:** Butterworth bandpass with adjustable order and cutoffs.
- **Metrics:** Mean/min/max HR, standard deviation as an HRV proxy, and bradycardia/normal/tachycardia classification.

## Project Structure

```
app.py             # Streamlit interface
models.py          # Time base, HR trajectory, ECG synthesis, filtering
utils.py           # Classification, text summaries, metric helpers
requirements.txt   # Python dependencies
main.lua           # Original Codespaces LÖVE sample (kept for reference)
```

## Educational Disclaimer

Bradycardia (<60 bpm), normal sinus rhythm (60-100 bpm), and tachycardia (>100 bpm) designations only scratch the surface. Real clinical evaluation also examines waveform morphology, symptoms, medications, comorbidities, and clinician judgment. Use this repository for coursework exploration, not diagnosis.

