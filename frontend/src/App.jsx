import { useState } from 'react';
import './App.css';
import pl from "./translations/pl.json";

const PL_NAMES = Object.fromEntries(
  Object.entries(pl).map(([key, value]) => [key.toLowerCase(), value])
);

function App() {
  const [showConfig, setShowConfig] = useState(false);
  const [endpointUrl, setEndpointUrl] = useState('http://127.0.0.1:8000/api/v1/product/recognize');
  const [fileFieldName, setFileFieldName] = useState('file');

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [responseFilename, setResponseFilename] = useState('');
  const [hasAnalyzed, setHasAnalyzed] = useState(false);

  // Wirtualna spiżarnia
  const [approvedList, setApprovedList] = useState([]);
  const [manualIngredient, setManualIngredient] = useState('');

  // Stan dla przepisów (zaślepki)
  const [recipes, setRecipes] = useState([]);
  const [isSearchingRecipes, setIsSearchingRecipes] = useState(false);

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
      setResponseFilename(data?.filename || '');

      let items = [];
      if (Array.isArray(data)) items = data;
      else if (data && Array.isArray(data.recognitions)) items = data.recognitions;
      else if (data && data.recognition && typeof data.recognition === 'object') items = [data.recognition];
      else if (data && Array.isArray(data.predictions)) items = data.predictions;
      else if (data && Array.isArray(data.results)) items = data.results;
      else if (data && typeof data === 'object') items = [data];

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

  const handleManualAdd = () => {
    const trimmed = manualIngredient.trim();
    if (trimmed) {
      addIngredient(trimmed);
      setManualIngredient('');
    }
  };

  // Symulacja wyszukiwania przepisów
  const handleSearchRecipes = () => {
    setIsSearchingRecipes(true);
    
    // Symulacja opóźnienia serwera (1.5 sekundy), żeby wyglądało realistycznie
    setTimeout(() => {
      setRecipes([
        {
          id: 1,
          name: 'Ekspresowa sałatka owocowo-warzywna',
          time: '10 min',
          difficulty: 'Bardzo łatwe',
          missing: ['Oliwa z oliwek', 'Orzechy włoskie'],
          emoji: '🥗'
        },
        {
          id: 2,
          name: 'Pożywna owsianka na mleku',
          time: '15 min',
          difficulty: 'Łatwe',
          missing: ['Płatki owsiane', 'Cynamon', 'Miód'],
          emoji: '🥣'
        },
        {
          id: 3,
          name: 'Domowa tarta rustykalna',
          time: '45 min',
          difficulty: 'Średnie',
          missing: ['Ciasto francuskie', 'Jajka', 'Śmietana 30%'],
          emoji: '🥧'
        }
      ]);
      setIsSearchingRecipes(false);
    }, 1500);
  };

  return (
    <>
      <nav className="navbar navbar-dark bg-success shadow-sm mb-4">
        <div className="container">
          <span className="navbar-brand fw-bold">
            System rekomendacji potraw – prototyp systemu rozpoznawania obrazów
          </span>
          <button className="btn btn-outline-light btn-sm" type="button" onClick={() => setShowConfig(!showConfig)}>
            Ustawienia Endpointu
          </button>
        </div>
      </nav>

      <div className="container pb-5">
        {showConfig && (
          <div className="mb-3">
            <div className="card card-body border-0 shadow-sm bg-white">
              <div className="row g-2 align-items-center">
                <div className="col-md-7">
                  <label className="form-label small fw-bold mb-1">Adres endpointu FastAPI:</label>
                  <input type="text" className="form-control form-control-sm" value={endpointUrl} onChange={(e) => setEndpointUrl(e.target.value)} />
                </div>
                <div className="col-md-5">
                  <label className="form-label small fw-bold mb-1">Nazwa parametru pliku w FastAPI:</label>
                  <input type="text" className="form-control form-control-sm" value={fileFieldName} onChange={(e) => setFileFieldName(e.target.value)} />
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="row g-4">
          <div className="col-md-6">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-header bg-white fw-bold py-3">1. Prześlij zdjęcie produktu spożywczego</div>
              <div className="card-body d-flex flex-column justify-content-between">
                <div>
                  <p className="text-muted small mb-2">Obsługiwane formaty: <strong>JPEG/JFIF, PNG, WEBP</strong> (maks. 8 MB)</p>
                  <input className="form-control mb-3" type="file" accept=".jfif,image/jpeg,image/jfif,image/png,image/webp" onChange={handleFileChange} />
                  {previewUrl && (
                    <div className="text-center my-3">
                      <img src={previewUrl} className="img-fluid preview-box" alt="Podgląd" />
                    </div>
                  )}
                </div>
                <button className="btn btn-success w-100 fw-bold py-2 mt-2" disabled={!selectedFile || isLoading} onClick={handleAnalyze}>
                  Rozpoznaj produkt
                </button>
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
                <span>2. Wynik analizy i Twoja spiżarnia</span>
                {responseFilename && <span className="badge bg-light text-secondary border fw-normal">Plik: {responseFilename}</span>}
              </div>
              <div className="card-body d-flex flex-column">
                
                <div style={{ minHeight: '180px' }}>
                  {!isLoading && !errorMsg && !hasAnalyzed && (
                    <div className="text-center text-muted my-4">
                      <p className="mb-1">Wgraj zdjęcie po lewej stronie i kliknij <strong>Rozpoznaj produkt</strong>.</p>
                      <small>Model wyświetli najbardziej prawdopodobne dopasowanie.</small>
                    </div>
                  )}
                  {isLoading && (
                    <div className="text-center my-4">
                      <div className="spinner-border text-success" role="status"></div>
                      <p className="mt-2 small text-muted">Trwa analiza obrazu przez sieć neuronową...</p>
                    </div>
                  )}
                  {errorMsg && (
                    <div className="alert alert-danger small"><strong>Błąd:</strong> {errorMsg}</div>
                  )}
                  {hasAnalyzed && !isLoading && (
                    <div>
                      <h6 className="fw-bold text-success mb-2">Rozpoznane opcje:</h6>
                      <div>
                        {predictions.map((item, index) => {
                          const rawName = item.product || item.label || item.class_name || item.class_id || 'Nieznany produkt';
                          const cleanKey = String(rawName).toLowerCase().replace(/^custom_/, '');
                          const displayName = PL_NAMES[cleanKey] || `${rawName}`;
                          const conf = item.confidence ?? item.probability ?? item.score ?? 0;
                          const percent = conf <= 1 ? (Number(conf) * 100).toFixed(1) : Number(conf).toFixed(1);
                          const badgeClass = index === 0 ? 'bg-success' : 'bg-secondary';
                          const borderClass = index === 0 ? 'border-success' : '';

                          return (
                            <div key={index} className={`card mb-2 ${borderClass}`}>
                              <div className="card-body py-1 px-2">
                                <div className="d-flex justify-content-between align-items-center mb-1">
                                  <span className="fw-bold small">{index + 1}. {displayName}</span>
                                  <span className={`badge ${badgeClass}`}>{percent}%</span>
                                </div>
                                <button className="btn btn-sm btn-outline-success py-0 w-100 mt-1" onClick={() => addIngredient(displayName)}>
                                  + Dodaj do spiżarni
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>

                <hr className="my-3" />

                <div className="mt-auto">
                  <div className="mb-3">
                    <label className="small fw-bold mb-1">Dodaj składnik ręcznie (jeśli brakuje na zdjęciu):</label>
                    <div className="input-group input-group-sm">
                      <input 
                        type="text" 
                        className="form-control" 
                        placeholder="np. Sól, Jajka, Czosnek..." 
                        value={manualIngredient}
                        onChange={(e) => setManualIngredient(e.target.value)}
                        onKeyDown={(e) => { if(e.key === 'Enter') handleManualAdd(); }}
                      />
                      <button className="btn btn-outline-success" type="button" onClick={handleManualAdd}>
                        Dodaj
                      </button>
                    </div>
                  </div>

                  <div>
                    <span className="small fw-bold">Twoja wirtualna spiżarnia:</span>
                    <div className="mt-2 border rounded p-2 bg-light" style={{ minHeight: '60px' }}>
                      {approvedList.length === 0 ? (
                        <span className="text-muted small">Spiżarnia jest pusta. Dodaj coś ze zdjęcia lub wpisz ręcznie.</span>
                      ) : (
                        approvedList.map((item, i) => (
                          <span key={i} className="badge bg-success me-1 mb-1 p-2">
                            {item}
                            <span style={{ cursor: 'pointer', marginLeft: '5px' }} onClick={() => removeIngredient(i)}>✕</span>
                          </span>
                        ))
                      )}
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>

        {/* PRZYCISK WYSZUKIWANIA I KARTY PRZEPISÓW */}
        <div className="row mt-4">
          <div className="col-12 text-center">
            <button 
              className="btn btn-lg btn-warning fw-bold px-5 shadow-sm"
              onClick={handleSearchRecipes}
              disabled={isSearchingRecipes || approvedList.length === 0}
            >
              {isSearchingRecipes ? (
                <><span className="spinner-border spinner-border-sm me-2"></span> Szukam najlepszych przepisów...</>
              ) : (
                'Szukaj przepisów z tych składników 🍽️'
              )}
            </button>
            {approvedList.length === 0 && (
              <div className="text-muted small mt-2">Dodaj przynajmniej jeden składnik do spiżarni, aby wyszukać przepisy.</div>
            )}
          </div>
        </div>

        {recipes.length > 0 && (
          <div className="row mt-4 g-4">
            <div className="col-12">
              <h4 className="fw-bold text-success mb-3">3. Rekomendowane przepisy dla Ciebie</h4>
            </div>
            {recipes.map((recipe) => (
              <div key={recipe.id} className="col-md-4">
                <div className="card h-100 border-0 shadow-sm recipe-card">
                  <div className="card-body text-center pb-2">
                    <div className="display-1 mb-3">{recipe.emoji}</div>
                    <h5 className="card-title fw-bold">{recipe.name}</h5>
                    <div className="d-flex justify-content-center gap-3 text-muted small mb-3">
                      <span>⏱️ {recipe.time}</span>
                      <span>📊 {recipe.difficulty}</span>
                    </div>
                  </div>
                  <div className="card-footer bg-white border-top-0 pt-0">
                    <div className="small fw-bold text-danger mb-1">Brakujące składniki:</div>
                    <div className="d-flex flex-wrap gap-1">
                      {recipe.missing.map((miss, idx) => (
                        <span key={idx} className="badge bg-light text-danger border border-danger">
                          {miss}
                        </span>
                      ))}
                    </div>
                    <button className="btn btn-outline-success w-100 mt-3 btn-sm fw-bold">
                      Zobacz pełny przepis
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}

export default App;