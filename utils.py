"""Helper utilities for classification, summaries, and quick metrics."""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


HR_CLASS_DESC = {
    "Bradycardia": "HR below 60 bpm often appears in endurance athletes or during sleep, but can also signal conduction issues.",
    "Normal": "HR between 60 and 100 bpm is considered a normal sinus rhythm at rest for most adults.",
    "Tachycardia": "HR above 100 bpm may reflect exercise, stress, fever, or arrhythmias depending on context.",
}


def compute_hr_metrics(heart_rate: np.ndarray) -> Dict[str, float]:
    """Return basic descriptive statistics for the heart-rate trace."""

    if heart_rate.size == 0:
        raise ValueError("heart_rate array must not be empty")

    metrics = {
        "mean": float(np.mean(heart_rate)),
        "min": float(np.min(heart_rate)),
        "max": float(np.max(heart_rate)),
        "std": float(np.std(heart_rate)),
    }
    return metrics


def classify_hr(mean_hr: float) -> Tuple[str, str]:
    """Classify heart rate into bradycardia, normal, or tachycardia."""

    if mean_hr < 60:
        cls = "Bradycardia"
    elif mean_hr <= 100:
        cls = "Normal"
    else:
        cls = "Tachycardia"

    return cls, HR_CLASS_DESC[cls]


def generate_summary_text(mean_hr: float, hr_class: str) -> str:
    """Return a concise educational explanation for the reported HR."""

    if hr_class == "Bradycardia":
        return (
            f"HR ≈ {mean_hr:.0f} bpm falls in the bradycardia range. This can be normal in well-trained "
            "athletes or during rest, but persistent low HR with symptoms warrants clinical attention."
        )
    if hr_class == "Normal":
        return (
            f"HR ≈ {mean_hr:.0f} bpm is within the expected resting range (60-100 bpm). Factors such as "
            "hydration, breathing, or mild stress can still nudge values slightly up or down."
        )
    return (
        f"HR ≈ {mean_hr:.0f} bpm indicates tachycardia. Exercise and stress are common causes, yet clinicians "
        "also evaluate fever, medications, or arrhythmias before acting."
    )


def educational_disclaimer() -> str:
    """Short reminder that the tool is an educational toy model."""

    return (
        "Educational demo only - not diagnostic. Real ECG interpretation considers morphology, symptoms, "
        "and patient history."
    )
