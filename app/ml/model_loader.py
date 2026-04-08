from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent / "lead_scoring_model.joblib"


class FallbackLeadScorer:
    # Predictable heuristic fallback for dev/test when no model exists.
    def predict_proba(self, rows: list[list[float]]) -> list[list[float]]:
        output: list[list[float]] = []
        for src_code, interactions, deal_value, first_response_hours in rows:
            score = 0.1 + 0.1 * interactions + 0.00001 * deal_value - 0.005 * first_response_hours + 0.05 * src_code
            score = max(0.0, min(0.99, score))
            output.append([1 - score, score])
        return output


def load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return FallbackLeadScorer()
