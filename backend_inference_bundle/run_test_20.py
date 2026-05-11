from __future__ import annotations

from pathlib import Path

import pandas as pd

from inference_dual_models import InferenceCoordinator


class BatchTestCoordinator:
    def __init__(self, input_csv: Path, output_csv: Path) -> None:
        self._input_csv = input_csv
        self._output_csv = output_csv
        self._inference = InferenceCoordinator()

    def run(self) -> None:
        df = pd.read_csv(self._input_csv)
        if "text" not in df.columns:
            raise ValueError("CSV must contain 'text' column")

        records = []
        for text in df["text"].fillna("").astype(str).tolist():
            result = self._inference.analyze_text(text)
            records.append(
                {
                    "text": text,
                    "priority_label": result["priority"]["label"],
                    "priority_score": result["priority"]["score"],
                    "sentiment_label": result["sentiment"]["label"],
                    "sentiment_score": result["sentiment"]["score"],
                }
            )

        out_df = pd.DataFrame(records)
        out_df.to_csv(self._output_csv, index=False, encoding="utf-8-sig")
        print(f"Saved: {self._output_csv}")


def main() -> None:
    root = Path(__file__).resolve().parent
    input_csv = root / "test_fragments_20.csv"
    output_csv = root / "test_results_20.csv"
    BatchTestCoordinator(input_csv, output_csv).run()


if __name__ == "__main__":
    main()
