from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

MODEL_PATH = Path(__file__).resolve().parent / "lead_scoring_model.joblib"


def build_synthetic_dataset(n_samples: int = 300):
    rng = np.random.default_rng(seed=42)
    lead_source = rng.integers(0, 4, size=n_samples)
    interaction_count = rng.integers(0, 12, size=n_samples)
    deal_value = rng.uniform(500, 50000, size=n_samples)
    time_to_first_response = rng.uniform(1, 120, size=n_samples)

    logits = (
        -1.2
        + 0.35 * lead_source
        + 0.28 * interaction_count
        + 0.00004 * deal_value
        - 0.03 * time_to_first_response
    )
    probability = 1 / (1 + np.exp(-logits))
    y = (probability > 0.5).astype(int)
    x = np.vstack([lead_source, interaction_count, deal_value, time_to_first_response]).T
    return x, y


def train_and_save_model() -> None:
    x, y = build_synthetic_dataset()
    model = LogisticRegression(max_iter=200)
    model.fit(x, y)
    joblib.dump(model, MODEL_PATH)


if __name__ == "__main__":
    train_and_save_model()
    print(f"Saved model to {MODEL_PATH}")
