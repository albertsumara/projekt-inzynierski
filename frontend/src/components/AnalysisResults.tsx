import type { AnalysisResultsProps } from "../types/recognition";

import PredictionCard from "./PredictionCard";
import SelectedIngredients from "./SelectedIngredients";

function AnalysisResults({
  predictions,
  approvedList,
  fileName,
  isLoading,
  error,
  addIngredient,
  removeIngredient,
}: AnalysisResultsProps) {
  const hasResults = predictions.length > 0;

  return (
    <div className="card border-0 shadow-sm h-100">
      <div className="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
        <span>2. Wynik analizy obrazu</span>

        {fileName && (
          <span className="badge bg-light text-secondary border fw-normal">
            Plik: {fileName}
          </span>
        )}
      </div>

      <div className="card-body">
        {isLoading && (
          <div className="text-center my-5">
            <div className="spinner-border text-success" role="status">
              <span className="visually-hidden">Ładowanie...</span>
            </div>

            <p className="mt-2 small text-muted">
              Trwa analiza obrazu przez sieć neuronową...
            </p>
          </div>
        )}

        {error && (
          <div className="alert alert-danger small">
            <strong>Nie udało się przeprowadzić analizy:</strong>

            <p className="mb-1">{error}</p>

            <small>
              Upewnij się, że serwer Uvicorn działa oraz w FastAPI
              skonfigurowano CORSMiddleware.
            </small>
          </div>
        )}

        {!isLoading && !error && !hasResults && (
          <div className="text-center text-muted my-5">
            <p className="mb-1">
              Wgraj zdjęcie po lewej stronie i kliknij{" "}
              <strong>Rozpoznaj produkt</strong>.
            </p>

            <small>
              Model wyświetli najbardziej prawdopodobne dopasowanie (1–3 opcje).
            </small>
          </div>
        )}

        {!isLoading && hasResults && (
          <div>
            <h6 className="fw-bold text-success mb-3">
              Rozpoznane opcje wg prawdopodobieństwa:
            </h6>

            {predictions.map((prediction, index) => (
              <PredictionCard
                key={index}
                prediction={prediction}
                index={index}
                onAdd={addIngredient}
              />
            ))}

            <hr className="my-3" />

            <div className="mb-2">
              <span className="small fw-bold">
                Twoje zatwierdzone składniki:
              </span>

              <SelectedIngredients
                ingredients={approvedList}
                onRemove={removeIngredient}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AnalysisResults;
