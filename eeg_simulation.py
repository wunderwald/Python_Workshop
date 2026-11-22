"""Simulated EEG data for the numpy practice."""

import numpy as np

CHANNELS = ["Fz", "Cz", "Pz", "Oz"]
SAMPLING_RATE = 100  # samples per second


def simulate_eeg(n_trials=20, seed=111):
    """
    Simulate EEG trials with a stimulus-locked brain response.

    Each trial lasts from -0.5 s to 1.49 s, the stimulus appears at 0 s.
    Every channel has its own offset, so the data needs a baseline correction.
    The brain response peaks around 0.35 s and is largest at Pz.

    Parameters
    ----------
    n_trials : int, optional
        Number of trials to simulate. Default is 20.
    seed : int, optional
        Seed for the random noise, so the data is the same every time. Default is 111.

    Returns
    -------
    trials : numpy.ndarray
        The EEG data in µV, shape (n_trials, 4 channels, 200 samples).
    channels : list of str
        The channel names.
    times : numpy.ndarray
        The time of each sample in seconds, shape (200,).
    """
    rng = np.random.default_rng(seed)

    times = np.arange(-50, 150) / SAMPLING_RATE

    # each channel has its own offset (in µV) => this is why we need baseline correction
    offsets = np.array([[12], [-8], [5], [20]])
    # the brain response to the stimulus: largest at Pz
    response_sizes = np.array([[2], [5], [8], [3]])
    response = np.exp(-((times - 0.35) ** 2) / (2 * 0.08 ** 2))  # a bump around 0.35 s
    alpha = np.sin(2 * np.pi * 10 * times)  # a 10 Hz oscillation

    trials = []
    for i in range(n_trials):
        noise = rng.normal(0, 1.5, size=(len(CHANNELS), len(times)))
        trials.append(offsets + response_sizes * response + alpha + noise)

    return np.array(trials), list(CHANNELS), times
