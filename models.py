"""Core physiological simulation utilities for BioSignal Studio.

This module groups time-base creation, heart-rate trajectories, ECG signal
synthesis, and optional filtering helpers. The math is intentionally
lightweight so students can trace how each parameter impacts the outputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy import signal


@dataclass
class SimulationResult:
    """Container for the raw simulation outputs."""

    time: np.ndarray
    heart_rate: np.ndarray
    ecg_raw: np.ndarray


def create_time_base(duration_s: float, fs: int = 300) -> np.ndarray:
    """Return an evenly spaced time vector for the simulation.

    Parameters
    ----------
    duration_s : float
        Total simulation time in seconds.
    fs : int, optional
        Sampling frequency in Hz. Typical ECG monitors use 250-500 Hz. The
        default of 300 Hz keeps plots smooth without being too heavy.
    """

    if duration_s <= 0:
        raise ValueError("duration_s must be positive")
    if fs <= 0:
        raise ValueError("fs must be positive")

    n_samples = int(duration_s * fs)
    return np.linspace(0, duration_s, n_samples, endpoint=False)


def simulate_heart_rate(
    time: np.ndarray,
    hr_rest: float,
    hr_peak: float,
    stress_level: float,
    tau: float = 4.0,
) -> np.ndarray:
    """Generate a smooth heart-rate trajectory using a simple exponential."""

    if hr_peak < hr_rest:
        hr_peak = hr_rest
    stress_frac = np.clip(stress_level / 100.0, 0.0, 1.0)
    target_hr = hr_rest + (hr_peak - hr_rest) * stress_frac
    tau = max(tau, 0.5)

    hr = target_hr - (target_hr - hr_rest) * np.exp(-time / tau)
    return hr


def _heartbeat_template(phase: np.ndarray) -> np.ndarray:
    """Return a simple ECG-like template built from Gaussians in phase space."""

    phase_mod = np.mod(phase, 2 * np.pi)
    p_wave = 0.1 * np.exp(-((phase_mod - 0.8) ** 2) / (2 * 0.05**2))
    q_wave = -0.15 * np.exp(-((phase_mod - 1.1) ** 2) / (2 * 0.02**2))
    r_wave = 1.2 * np.exp(-((phase_mod - 1.2) ** 2) / (2 * 0.01**2))
    s_wave = -0.25 * np.exp(-((phase_mod - 1.25) ** 2) / (2 * 0.02**2))
    t_wave = 0.25 * np.exp(-((phase_mod - 1.55) ** 2) / (2 * 0.08**2))

    base = 0.05 * np.sin(phase_mod)
    return base + p_wave + q_wave + r_wave + s_wave + t_wave


def generate_ecg_signal(
    time: np.ndarray,
    heart_rate: np.ndarray,
    noise_level: float = 0.05,
    baseline_wander: float = 0.1,
    seed: int | None = None,
) -> np.ndarray:
    """Create a synthetic ECG-like waveform aligned with the heart rate."""

    if time.ndim != 1 or heart_rate.ndim != 1:
        raise ValueError("time and heart_rate must be 1D arrays")
    if time.shape != heart_rate.shape:
        raise ValueError("time and heart_rate must match in length")

    dt = np.mean(np.diff(time))
    fs = 1.0 / dt
    freq = heart_rate / 60.0
    phase = np.cumsum(2 * np.pi * freq * dt)
    template = _heartbeat_template(phase)

    rng = np.random.default_rng(seed)
    noise = noise_level * rng.standard_normal(size=time.size)
    baseline = baseline_wander * np.sin(2 * np.pi * 0.2 * time)

    ecg = template + baseline + noise
    return ecg


def apply_bandpass_filter(
    signal_in: np.ndarray,
    fs: float,
    lowcut: float,
    highcut: float,
    order: int = 4,
) -> np.ndarray:
    """Apply a Butterworth bandpass filter to the ECG signal."""

    if lowcut <= 0 or highcut <= 0:
        raise ValueError("Cutoff frequencies must be positive")
    if highcut <= lowcut:
        raise ValueError("highcut must be greater than lowcut")

    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = signal.butter(order, [low, high], btype="bandpass")
    return signal.filtfilt(b, a, signal_in)


def run_simulation(
    duration_s: float,
    fs: int,
    hr_rest: float,
    hr_peak: float,
    stress_level: float,
    noise_level: float,
    baseline_wander: float,
    seed: int | None = None,
) -> SimulationResult:
    """Convenience wrapper that returns time, heart-rate, and ECG arrays."""

    time = create_time_base(duration_s, fs)
    hr = simulate_heart_rate(time, hr_rest, hr_peak, stress_level)
    ecg = generate_ecg_signal(time, hr, noise_level, baseline_wander, seed)
    return SimulationResult(time=time, heart_rate=hr, ecg_raw=ecg)
