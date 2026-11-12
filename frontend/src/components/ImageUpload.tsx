import { useState } from "react";
import type { ImageUploadProps } from "../types/recognition";

function ImageUpload({
  selectedFile,
  preview,
  isLoading,
  onFileChange,
  onAnalyze,
}: ImageUploadProps) {
  const [validationError, setValidationError] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;

    setValidationError("");

    if (!file) {
      onFileChange(null);
      return;
    }

    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];

    if (!allowedTypes.includes(file.type)) {
      setValidationError("Nieobsługiwany format. Wybierz JPEG, PNG lub WEBP.");
      onFileChange(null);
      event.target.value = "";
      return;
    }

    if (file.size > 8 * 1024 * 1024) {
      setValidationError("Plik jest za duży. Maksymalny rozmiar to 8 MB.");
      onFileChange(null);
      event.target.value = "";
      return;
    }

    onFileChange(file);
  };

  return (
    <div className="card border-0 shadow-sm h-100">
      <div className="card-header bg-white fw-bold py-3">
        1. Prześlij zdjęcie produktu spożywczego
      </div>

      <div className="card-body d-flex flex-column justify-content-between">
        <div>
          <p className="text-muted small mb-2">
            Obsługiwane formaty: <strong>JPEG, PNG, WEBP</strong> (maks. 8 MB)
          </p>

          <input
            className="form-control mb-3"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
          />

          {validationError && (
            <div className="alert alert-danger small">{validationError}</div>
          )}

          {preview && (
            <div className="text-center my-3">
              <img
                src={preview}
                className="img-fluid preview-box"
                alt="Podgląd produktu"
              />
            </div>
          )}
        </div>

        <button
          className="btn btn-success w-100 fw-bold py-2 mt-2"
          onClick={onAnalyze}
          disabled={!selectedFile || isLoading}
        >
          {isLoading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" />
              Analizowanie...
            </>
          ) : (
            "Rozpoznaj produkt"
          )}
        </button>
      </div>
    </div>
  );
}

export default ImageUpload;
