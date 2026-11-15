import { useState } from 'react';
import './App.css';

const PL_NAMES = {
  apple: 'Jabłko',
  granny_smith: 'Jabłko zielone Granny Smith',
  pear: 'Gruszka',
  plum: 'Śliwka',
  red_grapes: 'Czerwone winogrona',
  tomatoe: 'Pomidor',
  tomato: 'Pomidor',
  lemon: 'Cytryna',
  orange: 'Pomarańcza',
  banana: 'Banan',
  strawberry: 'Truskawka',
  pomegranate: 'Granat',
  fig: 'Figa',
  pineapple: 'Ananas',
  bell_pepper: 'Papryka',
  cucumber: 'Ogórek',
  broccoli: 'Brokuł',
};

function App() {
  // Ustawienia endpointu
  const [showConfig, setShowConfig] = useState(false);
  const [endpointUrl, setEndpointUrl] = useState('http://127.0.0.1:8000/api/v1/product/recognize');
  const [fileFieldName, setFileFieldName] = useState('file');

  // Wybrane zdjęcie i jego podgląd
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  // Stany ładowania, błędów i wyników z AI
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [responseFilename, setResponseFilename] = useState('');
  const [hasAnalyzed, setHasAnalyzed] = useState(false);

  // Lista zatwierdzonych składników
  const [approvedList, setApprovedList] = useState([]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setErrorMsg('');
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    } else {
      setSelectedFile(null);
      setPreviewUrl(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append(fileFieldName.trim() || 'file', selectedFile);

    setIsLoading(true);
    setErrorMsg('');
    setHasAnalyzed(false);

    try {
      const response = await fetch(endpointUrl.trim(), {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Błąd serwera (${response.status}): ${errText}`);
      }

      const data = await response.json();
      console.log('Odpowiedź z backendu:', data);

      setResponseFilename(data?.filename || '');

      // Rozpakowanie tablicy wyników tak samo jak w oryginale
      let items = [];
      if (Array.isArray(data)) {
        items = data;
      } else if (data && Array.isArray(data.recognitions)) {
        items = data.recognitions;
      } else if (data && data.recognition && typeof data.recognition === 'object') {
        items = [data.recognition];
      } else if (data && Array.isArray(data.predictions)) {
        items = data.predictions;
      } else if (data && Array.isArray(data.results)) {
        items = data.results;
      } else if (data && typeof data === 'object') {
        items = [data];
      }

      if (items.length === 0) {
        setErrorMsg('Serwer zwrócił pustą listę rozpoznań.');
        setPredictions([]);
      } else {
        setPredictions(items.slice(0, 3));
        setHasAnalyzed(true);
      }
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const addIngredient = (name) => {
    if (!approvedList.includes(name)) {
      setApprovedList([...approvedList, name]);
    }
  };

  const removeIngredient = (idxToRemove) => {
    setApprovedList(approvedList.filter((_, idx) => idx !== idxToRemove));
  };

  return (
    <>
      <nav className="navbar navbar-dark bg-success shadow-sm mb-4">
        <div className="container">
          <span className="navbar-brand fw-bold">
            System rekomendacji potraw – prototyp systemu rozpoznawania obrazów
          </span>
          <button
            className="btn btn-outline-light btn-sm"
            type="button"
            onClick={() => setShowConfig(!showConfig)}
          >
            Ustawienia Endpointu
          </button>
        </div>
      </nav>

      <div className="container">
        {showConfig && (
          <div className="mb-3">
            <div className="card card-body border-0 shadow-sm bg-white">
              <div className="row g-2 align-items-center">
                <div className="col-md-7">
                  <label className="form-label small fw-bold mb-1">Adres endpointu FastAPI:</label>
                  <input
                    type="text"
                    className="form-control form-control-sm"
                    value={endpointUrl}
                    onChange={(e) => setEndpointUrl(e.target.value)}
                  />
                </div>
                <div className="col-md-5">
                  <label className="form-label small fw-bold mb-1">
                    Nazwa parametru pliku w FastAPI:
                  </label>
                  <input
                    type="text"
                    className="form-control form-control-sm"
                    value={fileFieldName}
                    onChange={(e) => setFileFieldName(e.target.value)}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="row g-4">
          {/* Lewa kolumna: Przesyłanie zdjęcia */}
          <div className="col-md-6">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-header bg-white fw-bold py-3">
                Prześlij zdjęcie produktu spożywczego
              </div>
              <div className="card-body d-flex flex-column justify-content-between">
                <div>
                  <p className="text-muted small mb-2">
                    Obsługiwane formaty: <strong>JPEG/JFIF, PNG, WEBP</strong> (maks. 8 MB)
                  </p>
                  <input
                    className="form-control mb-3"
                    type="file"
                    accept=".jfif,image/jpeg,image/jfif,image/png,image/webp"
                    onChange={handleFileChange}
                  />

                  {previewUrl && (
                    <div className="text-center my-3">
                      <img src={previewUrl} className="img-fluid preview-box" alt="Podgląd produktu" />
                    </div>
                  )}
                </div>

                <button
                  className="btn btn-success w-100 fw-bold py-2 mt-2"
                  disabled={!selectedFile || isLoading}
                  onClick={handleAnalyze}
                >
                  Rozpoznaj produkt
                </button>
              </div>
            </div>
          </div>

          {/* Prawa kolumna: Wynik analizy */}
          <div className="col-md-6">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
                <span>2. Wynik analizy obrazu</span>
                {responseFilename && (
                  <span className="badge bg-light text-secondary border fw-normal">
                    Plik: {responseFilename}
                  </span>
                )}
              </div>
              <div className="card-body">
                {!isLoading && !errorMsg && !hasAnalyzed && (
                  <div className="text-center text-muted my-5">
                    <p className="mb-1">
                      Wgraj zdjęcie po lewej stronie i kliknij <strong>Rozpoznaj produkt</strong>.
                    </p>
                    <small>Model wyświetli najbardziej prawdopodobne dopasowanie (1–3 opcje).</small>
                  </div>
                )}

                {isLoading && (
                  <div className="text-center my-5">
                    <div className="spinner-border text-success" role="status"></div>
                    <p className="mt-2 small text-muted">
                      Trwa analiza obrazu przez sieć neuronową...
                    </p>
                  </div>
                )}

                {errorMsg && (
                  <div className="alert alert-danger small">
                    <strong>Nie udało się połączyć z endpointem:</strong> {errorMsg}
                    <br />
                    <small>
                      Upewnij się, że serwer Uvicorn działa oraz w FastAPI dodano{' '}
                      <code>CORSMiddleware</code>.
                    </small>
                  </div>
                )}

                {hasAnalyzed && !isLoading && (
                  <div>
                    <h6 className="fw-bold text-success mb-3">
                      Rozpoznane opcje wg prawdopodobieństwa:
                    </h6>

                    <div>
                      {predictions.map((item, index) => {
                        const rawName =
                          item.product ||
                          item.label ||
                          item.class_name ||
                          item.class_id ||
                          'Nieznany produkt';
                        const cleanKey = String(rawName).toLowerCase().replace(/^custom_/, '');
                        const displayName = PL_NAMES[cleanKey] || `🥗 ${rawName}`;

                        const conf = item.confidence ?? item.probability ?? item.score ?? 0;
                        const percent =
                          conf <= 1 ? (Number(conf) * 100).toFixed(1) : Number(conf).toFixed(1);

                        const badgeClass = index === 0 ? 'bg-success' : 'bg-secondary';
                        const borderClass = index === 0 ? 'border-success' : '';

                        return (
                          <div key={index} className={`card mb-2 ${borderClass}`}>
                            <div className="card-body py-2 px-3">
                              <div className="d-flex justify-content-between align-items-center mb-1">
                                <span className="fw-bold">
                                  {index + 1}. {displayName}
                                </span>
                                <span className={`badge ${badgeClass}`}>{percent}% pewności</span>
                              </div>
                              <div className="progress confidence-bar mb-2">
                                <div
                                  className={`progress-bar ${badgeClass}`}
                                  role="progressbar"
                                  style={{ width: `${Math.min(percent, 100)}%` }}
                                ></div>
                              </div>
                              <button
                                className="btn btn-sm btn-outline-success py-0"
                                onClick={() => addIngredient(displayName)}
                              >
                                + Wybierz ten produkt
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    <hr className="my-3" />
                    <div className="mb-2">
                      <span className="small fw-bold">Twoje zatwierdzone składniki:</span>
                      <div className="mt-2">
                        {approvedList.length === 0 ? (
                          <span className="text-muted small">Brak dodanych składników</span>
                        ) : (
                          approvedList.map((item, i) => (
                            <span key={i} className="badge bg-success me-1 mb-1 p-2">
                              {item}
                              <span
                                style={{ cursor: 'pointer', marginLeft: '5px' }}
                                onClick={() => removeIngredient(i)}
                              >
                                ✕
                              </span>
                            </span>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;