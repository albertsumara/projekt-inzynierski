import { useEffect, useState } from "react";

import Navbar from "./components/Navbar";
import ApiConfig from "./components/ApiConfig";
import ImageUpload from "./components/ImageUpload";
import AnalysisResults from "./components/AnalysisResults";

import type { Prediction, AnalysisResultsProps } from "./types/recognition";

import "./App.css";

const DEFAULT_ENDPOINT = "http://127.0.0.1:8000/api/v1/product/recognize";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function extractPredictions(data: unknown): Prediction[] {
  if (Array.isArray(data)) {
    return data as Prediction[];
  }

  if (!isRecord(data)) {
    return [];
  }

  if (Array.isArray(data.recognitions)) {
    return data.recognitions as Prediction[];
  }

  if (isRecord(data.recognition)) {
    return [data.recognition as Prediction];
  }

  if (Array.isArray(data.predictions)) {
    return data.predictions as Prediction[];
  }

  if (Array.isArray(data.results)) {
    return data.results as Prediction[];
  }

  if (
    "product" in data ||
    "label" in data ||
    "class_name" in data ||
    "class_id" in data
  ) {
    return [data as Prediction];
  }

  return [];
}

function App() {
  const [endpointUrl, setEndpointUrl] = useState(DEFAULT_ENDPOINT);

  const [fileFieldName, setFileFieldName] = useState("file");

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [preview, setPreview] = useState<string | null>(null);

  const [predictions, setPredictions] = useState<Prediction[]>([]);

  const [fileName, setFileName] = useState("");

  const [approvedList, setApprovedList] = useState<string[]>([]);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!selectedFile) {
      setPreview(null);
      return;
    }

    const objectUrl = URL.createObjectURL(selectedFile);

    setPreview(objectUrl);

    return () => {
      URL.revokeObjectURL(objectUrl);
    };
  }, [selectedFile]);

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    setPredictions([]);
    setApprovedList([]);
    setError("");
    setFileName(file?.name ?? "");
  };

  const handleAnalyze = async () => {
    if (!selectedFile || isLoading) return;

    setIsLoading(true);
    setError("");
    setPredictions([]);
    setApprovedList([]);

    const formData = new FormData();

    formData.append(fileFieldName.trim() || "file", selectedFile);

    try {
      const response = await fetch(endpointUrl.trim(), {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorMessage = await response.text();

        throw new Error(`Błąd serwera (${response.status}): ${errorMessage}`);
      }

      const data: unknown = await response.json();

      console.log("Odpowiedź z backendu:", data);

      const items = extractPredictions(data);

      if (items.length === 0) {
        throw new Error("Serwer zwrócił pustą listę rozpoznań.");
      }

      setPredictions(items.slice(0, 3));

      if (isRecord(data) && typeof data.filename === "string") {
        setFileName(data.filename);
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Wystąpił nieznany błąd.";

      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const addIngredient = (name: string) => {
    setApprovedList((previous) =>
      previous.includes(name) ? previous : [...previous, name],
    );
  };

  const removeIngredient = (name: string) => {
    setApprovedList((previous) => previous.filter((item) => item !== name));
  };

  return (
    <>
      <Navbar />

      <main className="container">
        <ApiConfig
          endpointUrl={endpointUrl}
          setEndpointUrl={setEndpointUrl}
          fileFieldName={fileFieldName}
          setFileFieldName={setFileFieldName}
        />

        <div className="row g-4">
          <div className="col-md-6">
            <ImageUpload
              selectedFile={selectedFile}
              preview={preview}
              isLoading={isLoading}
              onFileChange={handleFileChange}
              onAnalyze={handleAnalyze}
            />
          </div>

          <div className="col-md-6">
            <AnalysisResults
              predictions={predictions}
              approvedList={approvedList}
              fileName={fileName}
              isLoading={isLoading}
              error={error}
              addIngredient={addIngredient}
              removeIngredient={removeIngredient}
            />
          </div>
        </div>
      </main>
    </>
  );
}

export default App;
