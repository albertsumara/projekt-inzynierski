export interface Prediction {
  product?: string;
  label?: string;
  class_name?: string;
  class_id?: string;

  confidence?: number;
  probability?: number;
  score?: number;
}

export interface RecognitionResponse {
  filename?: string;
  recognitions?: Prediction[];
  recognition?: Prediction;
  predictions?: Prediction[];
  results?: Prediction[];
}

export type ApiResponse = Prediction[] | RecognitionResponse;

export interface ApiConfigProps {
  endpointUrl: string;
  setEndpointUrl: (url: string) => void;
  fileFieldName: string;
  setFileFieldName: (name: string) => void;
}

export interface ImageUploadProps {
  selectedFile: File | null;
  preview: string | null;
  isLoading: boolean;
  onFileChange: (file: File | null) => void;
  onAnalyze: () => void;
}

export interface AnalysisResultsProps {
  predictions: Prediction[];
  approvedList: string[];
  fileName: string;
  isLoading: boolean;
  error: string;
  addIngredient: (name: string) => void;
  removeIngredient: (name: string) => void;
}
