"""Streamlit front-end for the BioSignal Studio decision helper."""
from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from models import apply_bandpass_filter, run_simulation
from utils import (
    classify_hr,
    compute_hr_metrics,
    educational_disclaimer,
    generate_summary_text,
)


def _sidebar_controls() -> dict:
    """Render the sidebar widgets and return the chosen parameters."""

    st.sidebar.header("Simulation Parameters")
    rest_hr = st.sidebar.slider("Resting heart rate (bpm)", 50, 90, 70)
    peak_hr = st.sidebar.slider("Peak/exercise heart rate (bpm)", 90, 170, 130)
    stress = st.sidebar.slider("Stress / exercise level (%)", 0, 100, 40)
    duration = st.sidebar.slider("Simulation duration (s)", 5, 30, 12)
    fs = st.sidebar.slider("Sampling rate (Hz)", 200, 400, 300)
    noise = st.sidebar.slider("Noise level", 0.0, 1.0, 0.15)
    baseline = st.sidebar.slider("Baseline wander amplitude", 0.0, 1.0, 0.2)

    st.sidebar.header("Filtering Options")
    apply_filter = st.sidebar.checkbox("Apply bandpass filter", value=True)
    lowcut = st.sidebar.slider("Low cutoff (Hz)", 0.5, 5.0, 0.8)
    highcut = st.sidebar.slider("High cutoff (Hz)", 15.0, 40.0, 30.0)
    order = st.sidebar.selectbox("Filter order", options=[2, 4, 6], index=1)

    st.sidebar.button(
        "Run Simulation",
        help="Streamlit already reruns automatically, but this button makes the workflow explicit.",
    )

    params = {
        "rest_hr": rest_hr,
        "peak_hr": peak_hr,
        "stress": stress,
        "duration": duration,
        "fs": fs,
        "noise": noise,
        "baseline": baseline,
        "apply_filter": apply_filter,
        "lowcut": lowcut,
        "highcut": highcut,
        "order": order,
    }
    return params


def _plot_signals(time, raw, filtered):
    """Plot raw/filtered ECG and HR in stacked rows."""

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(time, raw, label="Raw ECG", color="#1f77b4", linewidth=1)
    if filtered is not None:
        ax.plot(time, filtered, label="Filtered ECG", color="#d62728", linewidth=1)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (a.u.)")
    ax.set_title("Synthetic ECG signal")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.2)
    st.pyplot(fig, clear_figure=True)


def _plot_hr(time, hr):
    """Plot the heart-rate trajectory."""

    fig, ax = plt.subplots(figsize=(10, 2.6))
    ax.plot(time, hr, color="#2ca02c")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Heart rate (bpm)")
    ax.set_title("Modeled heart-rate response")
    ax.grid(alpha=0.2)
    st.pyplot(fig, clear_figure=True)


def main() -> None:
    st.set_page_config(page_title="BioSignal Studio", layout="wide")
    params = _sidebar_controls()

    st.title("BioSignal Studio - Heart Rate & ECG Decision Helper")
    st.caption(
        "Explore how heart rate (beats per minute) and an ECG waveform respond to stress, noise, and simple filtering. "
        "ECG stands for electrocardiogram and records the heart's electrical activity. This dashboard is an educational sandbox, not a clinical tool."
    )

    result = run_simulation(
        duration_s=params["duration"],
        fs=params["fs"],
        hr_rest=params["rest_hr"],
        hr_peak=params["peak_hr"],
        stress_level=params["stress"],
        noise_level=params["noise"],
        baseline_wander=params["baseline"],
        seed=42,
    )

    filtered_signal = None
    if params["apply_filter"]:
        highcut = max(params["highcut"], params["lowcut"] + 1.0)  # keep passband valid
        filtered_signal = apply_bandpass_filter(
            result.ecg_raw,
            fs=params["fs"],
            lowcut=params["lowcut"],
            highcut=highcut,
            order=params["order"],
        )

    metrics = compute_hr_metrics(result.heart_rate)
    hr_class, class_desc = classify_hr(metrics["mean"])
    summary_text = generate_summary_text(metrics["mean"], hr_class)

    signals_tab, summary_tab = st.tabs(["Signals", "Summary & Interpretation"])

    with signals_tab:
        st.subheader("Modeled Signals")
        _plot_signals(result.time, result.ecg_raw, filtered_signal)
        _plot_hr(result.time, result.heart_rate)
        with st.expander("What am I looking at?", expanded=False):
            st.write(
                "The top plot shows a synthetic ECG that mimics P-QRS-T features with added noise and baseline drift. "
                "If filtering is active, the red trace removes slow drift and high-frequency noise. The bottom plot charts the heart-rate trajectory as it ramps from the resting value toward the stress-adjusted target."
            )

    with summary_tab:
        st.subheader("Quick Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Mean HR", f"{metrics['mean']:.0f} bpm")
        col2.metric("Min HR", f"{metrics['min']:.0f} bpm")
        col3.metric("Max HR", f"{metrics['max']:.0f} bpm")
        st.metric("HRV proxy (std)", f"{metrics['std']:.1f} bpm")

        st.markdown(f"**Classification:** {hr_class}")
        st.write(class_desc)
        st.write(summary_text)
        st.info(
            "Bradycardia < 60 bpm, Normal 60-100 bpm, Tachycardia > 100 bpm. Clinicians also inspect wave morphology, symptoms, and patient history."
        )
        st.warning(educational_disclaimer())

    st.caption(
        "Model assumptions: exponential HR rise with stress, Gaussian-shaped ECG beats, optional Butterworth filtering. "
        "Use this as a storytelling aid for lab reports or presentations."
    )


if __name__ == "__main__":
    main()
