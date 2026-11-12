import type { Prediction } from "../types/recognition";
import { translateProductName, getConfidence } from "../utils/productNames";

interface PredictionCardProps {
  prediction: Prediction;
  index: number;
  onAdd: (name: string) => void;
}

function PredictionCard({ prediction, index, onAdd }: PredictionCardProps) {
  const rawName =
    prediction.product ??
    prediction.label ??
    prediction.class_name ??
    prediction.class_id?.toString() ??
    "Nieznany produkt";

  const displayName = translateProductName(String(rawName));

  const percent = getConfidence(prediction);

  const isBestPrediction = index === 0;

  const badgeClass = isBestPrediction ? "bg-success" : "bg-secondary";

  return (
    <div className={`card mb-2 ${isBestPrediction ? "border-success" : ""}`}>
      <div className="card-body py-2 px-3">
        <div className="d-flex justify-content-between align-items-center mb-1">
          <span className="fw-bold">
            {index + 1}. {displayName}
          </span>

          <span className={`badge ${badgeClass}`}>
            {percent.toFixed(1)}% pewności
          </span>
        </div>

        <div className="progress confidence-bar mb-2">
          <div
            className={`progress-bar ${badgeClass}`}
            role="progressbar"
            style={{ width: `${percent}%` }}
            aria-valuenow={percent}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>

        <button
          className="btn btn-sm btn-outline-success py-0"
          onClick={() => onAdd(displayName)}
        >
          + Wybierz ten produkt
        </button>
      </div>
    </div>
  );
}

export default PredictionCard;
