import { useState, useEffect, useMemo } from "react";
import plTranslations from "./translations/pl.json";
import recipesData from "./data/receipes.json";

const STORAGE_PROFILE_KEY = "diet_app_user_profile_v1";
const STORAGE_LOG_KEY = "diet_app_daily_log_v1";

const MEAL_PRESETS = {
  breakfast: { label: "Śniadanie", ratio: 0.25 },
  lunch: { label: "Obiad", ratio: 0.4 },
  dinner: { label: "Kolacja", ratio: 0.25 },
  snack: { label: "Przekąska", ratio: 0.1 },
  custom: { label: "Własne kcal", ratio: null },
};

const getTodayKey = () => new Date().toISOString().split("T")[0];

// standarize polish suffix ( Jajka -> jajk, Jajko -> jajk, Pomidory -> pomidor etc)
const normalizePl = (str) => {
  const s = str.toLowerCase().trim();
  if (s.length <= 4) return s;
  return s.replace(/(ami|ach|om|ów|em|ie|y|i|a|e|ę|ą|o|u)$/g, "");
};

export default function App() {
  // api
  const [showSettings, setShowSettings] = useState(false);
  const [endpointUrl, setEndpointUrl] = useState(
    "http://127.0.0.1:8000/api/v1/product/recognize",
  );
  const [fileParamName, setFileParamName] = useState("file");

  // user profile in localstorage
  const [profile, setProfile] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_PROFILE_KEY);
      if (saved) return JSON.parse(saved);
    } catch {
      // ignores reading errors
    }
    return {
      gender: "male",
      age: 23,
      weight: 78,
      height: 180,
      activity: 1.55,
      goal: "maintain",
      isVegetarian: false,
      isGlutenFree: false,
      mealType: "lunch",
      customMealKcal: 600,
    };
  });

  // calories per day
  const [eatenMeals, setEatenMeals] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_LOG_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.date === getTodayKey() && Array.isArray(parsed.meals)) {
          return parsed.meals;
        }
      }
    } catch {
      // ignores reading errors
    }
    return [];
  });

  const [showTodayLog, setShowTodayLog] = useState(false);
  const [justLoggedId, setJustLoggedId] = useState(null);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_PROFILE_KEY, JSON.stringify(profile));
    } catch {
      // ignores reading errors
    }
  }, [profile]);

  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_LOG_KEY,
        JSON.stringify({ date: getTodayKey(), meals: eatenMeals }),
      );
    } catch {
      // ignores reading errors
    }
  }, [eatenMeals]);

  // image recognition
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [predictions, setPredictions] = useState([]);
  const [apiError, setApiError] = useState(null);

  // pantry
  const [pantry, setPantry] = useState([]);
  const [manualIngredient, setManualIngredient] = useState("");

  // recommended recipes
  const [recommendedRecipes, setRecommendedRecipes] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [expandedRecipeId, setExpandedRecipeId] = useState(null);

  // calories calculator MIFFLIN-ST JEOR
  const dailyTargetKcal = useMemo(() => {
    const w = Number(profile.weight) || 70;
    const h = Number(profile.height) || 175;
    const a = Number(profile.age) || 25;
    const act = Number(profile.activity) || 1.55;

    const bmr =
      profile.gender === "female"
        ? 10 * w + 6.25 * h - 5 * a - 161
        : 10 * w + 6.25 * h - 5 * a + 5;

    let tdee = bmr * act;
    if (profile.goal === "lose") tdee -= 400;
    if (profile.goal === "gain") tdee += 300;

    return Math.max(1200, Math.round(tdee));
  }, [profile]);

  const consumedTotals = useMemo(() => {
    return eatenMeals.reduce(
      (acc, meal) => ({
        calories: acc.calories + (Number(meal.calories) || 0),
        protein: acc.protein + (Number(meal.protein) || 0),
        fat: acc.fat + (Number(meal.fat) || 0),
        carbs: acc.carbs + (Number(meal.carbs) || 0),
      }),
      { calories: 0, protein: 0, fat: 0, carbs: 0 },
    );
  }, [eatenMeals]);

  const remainingKcal = dailyTargetKcal - consumedTotals.calories;

  const { targetMealKcal, wasCappedByRemaining } = useMemo(() => {
    const preset = MEAL_PRESETS[profile.mealType] || MEAL_PRESETS.lunch;
    const rawTarget =
      profile.mealType === "custom"
        ? Math.max(50, Number(profile.customMealKcal) || 500)
        : Math.round(dailyTargetKcal * preset.ratio);

    if (remainingKcal > 0 && rawTarget > remainingKcal) {
      return { targetMealKcal: remainingKcal, wasCappedByRemaining: true };
    }
    return { targetMealKcal: rawTarget, wasCappedByRemaining: false };
  }, [
    profile.mealType,
    profile.customMealKcal,
    dailyTargetKcal,
    remainingKcal,
  ]);

  const updateProfile = (field, value) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
  };

  // image handling
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setPredictions([]);
    setApiError(null);
  };

  const translateLabel = (rawClass) => {
    if (!rawClass) return "";
    const normalized = rawClass.toLowerCase().trim();
    if (plTranslations[rawClass]) return plTranslations[rawClass];
    if (plTranslations[normalized]) return plTranslations[normalized];
    return (
      rawClass.charAt(0).toUpperCase() + rawClass.slice(1).replace(/_/g, " ")
    );
  };

  const handleRecognize = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setApiError(null);

    try {
      const formData = new FormData();
      formData.append(fileParamName, selectedFile);

      const response = await fetch(endpointUrl, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Błąd serwera (${response.status})`);
      }

      const data = await response.json();

      // results list regardless of input names in fastapi
      const rawList = Array.isArray(data)
        ? data
        : data.predictions ||
          data.results ||
          data.top_predictions ||
          data.items ||
          Object.values(data).find((val) => Array.isArray(val)) ||
          [];

      if (rawList.length === 0) {
        setApiError(
          `Serwer odpowiedział, ale nie znaleziono listy predykcji: ${JSON.stringify(data)}`,
        );
      }
      setPredictions(rawList);
    } catch (err) {
      setApiError(
        err.message ||
          "Nie udało się połączyć z backendem. Możesz dodać składniki ręcznie poniżej.",
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  //  pantry handling
  const addToPantry = (item) => {
    const cleaned = item.trim();
    if (!cleaned) return;
    const formatted =
      cleaned.charAt(0).toUpperCase() + cleaned.slice(1).toLowerCase();
    setPantry((prev) =>
      prev.some((p) => p.toLowerCase() === formatted.toLowerCase())
        ? prev
        : [...prev, formatted],
    );
  };

  const removeFromPantry = (itemToRemove) => {
    setPantry((prev) => prev.filter((item) => item !== itemToRemove));
  };

  const handleManualAdd = (e) => {
    e.preventDefault();
    if (!manualIngredient.trim()) return;
    manualIngredient
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)
      .forEach(addToPantry);
    setManualIngredient("");
  };

  // receipes handling
  const handleSearchRecipes = () => {
    if (pantry.length === 0) return;

    const pantryNormalized = pantry.map((p) => ({
      raw: p.toLowerCase().trim(),
      stem: normalizePl(p),
    }));

    const recipesList = Array.isArray(recipesData)
      ? recipesData
      : recipesData.recipes || [];

    const scored = recipesList
      .filter((recipe) => {
        const isVeg = recipe.isVegetarian ?? recipe.vegetarian ?? true;
        const isGF = recipe.isGlutenFree ?? recipe.glutenFree ?? true;
        if (profile.isVegetarian && !isVeg) return false;
        if (profile.isGlutenFree && !isGF) return false;
        return true;
      })
      .map((recipe) => {
        const rawIngredients = Array.isArray(recipe.ingredients)
          ? recipe.ingredients
          : [];
        const ingredientNames = rawIngredients.map((ing) =>
          typeof ing === "string" ? ing : ing.name,
        );

        const matched = [];
        const missing = [];

        ingredientNames.forEach((ingName) => {
          const ingLower = ingName.toLowerCase().trim();
          const ingStem = normalizePl(ingName);

          const hasIt = pantryNormalized.some(
            (p) =>
              ingLower.includes(p.raw) ||
              p.raw.includes(ingLower) ||
              (ingStem.length >= 4 &&
                p.stem.length >= 4 &&
                (ingStem === p.stem ||
                  ingStem.startsWith(p.stem) ||
                  p.stem.startsWith(ingStem))),
          );

          if (hasIt) matched.push(ingName);
          else missing.push(ingName);
        });

        const totalIng = ingredientNames.length || 1;
        const ingredientRatio = matched.length / totalIng;

        const recipeKcal = Number(recipe.calories) || 0;
        const kcalDiff = Math.abs(recipeKcal - targetMealKcal);
        const kcalScore = Math.max(
          0,
          1 - kcalDiff / Math.max(targetMealKcal, 300),
        );

        const matchPercent = Math.round(
          (ingredientRatio * 0.7 + kcalScore * 0.3) * 100,
        );

        return {
          ...recipe,
          title: recipe.title || recipe.name,
          emoji: recipe.emoji || recipe.icon || "🍽️",
          prepTime: recipe.prepTime || recipe.time || "20 min",
          matchedCount: matched.length,
          totalCount: totalIng,
          missingIngredients: missing,
          matchPercent,
        };
      })
      .filter((r) => r.matchedCount > 0)
      .sort((a, b) => b.matchPercent - a.matchPercent);

    setRecommendedRecipes(scored);
    setHasSearched(true);
  };

  // logging the meal
  const handleLogMeal = (recipe) => {
    const newEntry = {
      logId: `${recipe.id || recipe.title}-${Date.now()}`,
      title: recipe.title,
      emoji: recipe.emoji,
      calories: Number(recipe.calories) || 0,
      protein: Number(recipe.protein) || 0,
      fat: Number(recipe.fat) || 0,
      carbs: Number(recipe.carbs) || 0,
      mealTypeLabel: MEAL_PRESETS[profile.mealType]?.label || "Posiłek",
      time: new Date().toLocaleTimeString("pl-PL", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    setEatenMeals((prev) => [...prev, newEntry]);
    setJustLoggedId(recipe.id || recipe.title);
    setTimeout(() => setJustLoggedId(null), 1800);
  };

  const handleRemoveLoggedMeal = (logId) => {
    setEatenMeals((prev) => prev.filter((m) => m.logId !== logId));
  };

  const progressPercent = Math.min(
    100,
    Math.round((consumedTotals.calories / dailyTargetKcal) * 100),
  );
  const isOverLimit = remainingKcal < 0;

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.headerTitle}>
          System rekomendacji potraw – prototyp systemu rozpoznawania obrazów
        </h1>
        <button
          onClick={() => setShowSettings((s) => !s)}
          style={styles.settingsBtn}
        >
          Ustawienia Endpointu
        </button>
      </header>

      <main style={styles.container}>
        {showSettings && (
          <section style={styles.card}>
            <div style={styles.twoCol}>
              <div>
                <label style={styles.label}>Adres endpointu FastAPI:</label>
                <input
                  type="text"
                  value={endpointUrl}
                  onChange={(e) => setEndpointUrl(e.target.value)}
                  style={styles.input}
                />
              </div>
              <div>
                <label style={styles.label}>
                  Nazwa parametru pliku w FastAPI:
                </label>
                <input
                  type="text"
                  value={fileParamName}
                  onChange={(e) => setFileParamName(e.target.value)}
                  style={styles.input}
                />
              </div>
            </div>
          </section>
        )}

        <section style={styles.card}>
          <div style={styles.profileGrid}>
            <div>
              <label style={styles.smallLabel}>Płeć</label>
              <select
                value={profile.gender}
                onChange={(e) => updateProfile("gender", e.target.value)}
                style={styles.input}
              >
                <option value="male">Mężczyzna</option>
                <option value="female">Kobieta</option>
              </select>
            </div>
            <div>
              <label style={styles.smallLabel}>Wiek (lata)</label>
              <input
                type="number"
                min="14"
                max="100"
                value={profile.age}
                onChange={(e) => updateProfile("age", e.target.value)}
                style={styles.input}
              />
            </div>
            <div>
              <label style={styles.smallLabel}>Waga (kg)</label>
              <input
                type="number"
                min="35"
                max="250"
                value={profile.weight}
                onChange={(e) => updateProfile("weight", e.target.value)}
                style={styles.input}
              />
            </div>
            <div>
              <label style={styles.smallLabel}>Wzrost (cm)</label>
              <input
                type="number"
                min="120"
                max="230"
                value={profile.height}
                onChange={(e) => updateProfile("height", e.target.value)}
                style={styles.input}
              />
            </div>
            <div>
              <label style={styles.smallLabel}>Aktywność</label>
              <select
                value={profile.activity}
                onChange={(e) =>
                  updateProfile("activity", Number(e.target.value))
                }
                style={styles.input}
              >
                <option value={1.2}>Niska (praca siedząca)</option>
                <option value={1.375}>Lekka (1-2 treningi)</option>
                <option value={1.55}>Umiarkowana (3-4 treningi)</option>
                <option value={1.725}>Wysoka (5+ treningów)</option>
              </select>
            </div>
            <div>
              <label style={styles.smallLabel}>Cel sylwetkowy</label>
              <select
                value={profile.goal}
                onChange={(e) => updateProfile("goal", e.target.value)}
                style={styles.input}
              >
                <option value="lose">Redukcja (-400 kcal)</option>
                <option value="maintain">Utrzymanie wagi</option>
                <option value="gain">Masa (+300 kcal)</option>
              </select>
            </div>
          </div>

          <div style={styles.mealRow}>
            <div style={styles.mealButtonsWrap}>
              <span style={styles.smallLabel}>Szukam na:</span>
              {Object.entries(MEAL_PRESETS).map(([key, info]) => {
                const active = profile.mealType === key;
                return (
                  <button
                    key={key}
                    type="button"
                    onClick={() => updateProfile("mealType", key)}
                    style={{
                      ...styles.mealChip,
                      backgroundColor: active ? "#2e7d32" : "#f1f5f9",
                      color: active ? "#fff" : "#334155",
                      borderColor: active ? "#2e7d32" : "#cbd5e1",
                    }}
                  >
                    {info.label}
                    {info.ratio ? ` (${Math.round(info.ratio * 100)}%)` : ""}
                  </button>
                );
              })}

              {profile.mealType === "custom" && (
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <input
                    type="number"
                    min="100"
                    max="2500"
                    step="50"
                    value={profile.customMealKcal}
                    onChange={(e) =>
                      updateProfile("customMealKcal", e.target.value)
                    }
                    style={{ ...styles.input, width: 90, padding: "5px 8px" }}
                  />
                  <span style={{ fontSize: 13, color: "#475569" }}>kcal</span>
                </div>
              )}
            </div>

            <div style={styles.dietToggles}>
              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={profile.isVegetarian}
                  onChange={(e) =>
                    updateProfile("isVegetarian", e.target.checked)
                  }
                />
                Wegetariańska
              </label>
              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={profile.isGlutenFree}
                  onChange={(e) =>
                    updateProfile("isGlutenFree", e.target.checked)
                  }
                />
                Bez glutenu
              </label>
            </div>
          </div>

          <div style={styles.dailyBox}>
            <div style={styles.dailyHeader}>
              <div>
                <strong>Dzienna pula ({getTodayKey()}): </strong>
                <span>
                  Zjedzono{" "}
                  <strong
                    style={{ color: isOverLimit ? "#dc2626" : "#2e7d32" }}
                  >
                    {consumedTotals.calories}
                  </strong>{" "}
                  / {dailyTargetKcal} kcal
                </span>
                <span
                  style={{ marginLeft: 12, color: "#475569", fontSize: 13 }}
                >
                  (B: {consumedTotals.protein}g | T: {consumedTotals.fat}g | W:{" "}
                  {consumedTotals.carbs}g)
                </span>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span
                  style={{
                    fontWeight: 700,
                    color: isOverLimit ? "#dc2626" : "#15803d",
                    fontSize: 14,
                  }}
                >
                  {isOverLimit
                    ? `Przekroczono o ${Math.abs(remainingKcal)} kcal`
                    : `Pozostało: ${remainingKcal} kcal`}
                </span>
                {eatenMeals.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setShowTodayLog((s) => !s)}
                    style={styles.logToggleBtn}
                  >
                    {showTodayLog
                      ? "Ukryj zjedzone"
                      : `Zjedzone dziś (${eatenMeals.length})`}
                  </button>
                )}
              </div>
            </div>

            <div style={styles.progressTrack}>
              <div
                style={{
                  ...styles.progressFill,
                  width: `${progressPercent}%`,
                  backgroundColor: isOverLimit ? "#dc2626" : "#2e7d32",
                }}
              />
            </div>

            <div style={styles.targetInfo}>
              Cel na ten posiłek: <strong>{targetMealKcal} kcal</strong>
              {wasCappedByRemaining && (
                <span style={{ color: "#b45309", marginLeft: 6 }}>
                  (dopasowano automatycznie do pozostałego limitu dziennego)
                </span>
              )}
            </div>

            {showTodayLog && eatenMeals.length > 0 && (
              <div style={styles.logList}>
                {eatenMeals.map((m) => (
                  <div key={m.logId} style={styles.logItem}>
                    <span>
                      {m.emoji} <strong>{m.title}</strong>{" "}
                      <span style={{ color: "#64748b", fontSize: 12 }}>
                        ({m.mealTypeLabel}, {m.time})
                      </span>
                    </span>
                    <div
                      style={{ display: "flex", alignItems: "center", gap: 10 }}
                    >
                      <span style={{ fontWeight: 600, fontSize: 13 }}>
                        {m.calories} kcal
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveLoggedMeal(m.logId)}
                        title="Usuń z dziennika"
                        style={styles.removeLogBtn}
                      >
                        ×
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        <div style={styles.twoCol}>
          <section style={styles.card}>
            <h2 style={styles.cardTitle}>
              1. Prześlij zdjęcie produktu spożywczego
            </h2>
            <p style={styles.hint}>
              Obsługiwane formaty: <strong>JPEG/JFIF, PNG, WEBP</strong> (maks.
              8 MB)
            </p>

            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
              style={styles.fileInput}
            />

            {previewUrl && (
              <div style={styles.previewBox}>
                <img
                  src={previewUrl}
                  alt="Podgląd produktu"
                  style={styles.previewImg}
                />
              </div>
            )}

            <button
              onClick={handleRecognize}
              disabled={!selectedFile || isAnalyzing}
              style={{
                ...styles.primaryBtn,
                opacity: !selectedFile || isAnalyzing ? 0.65 : 1,
                cursor:
                  !selectedFile || isAnalyzing ? "not-allowed" : "pointer",
              }}
            >
              {isAnalyzing ? "Analizowanie..." : "🔍 Rozpoznaj produkt"}
            </button>
          </section>

          <section style={styles.card}>
            <div style={styles.cardHeaderRow}>
              <h2 style={styles.cardTitle}>
                2. Wynik analizy i Twoja spiżarnia
              </h2>
              {selectedFile && (
                <span style={styles.fileBadge}>Plik: {selectedFile.name}</span>
              )}
            </div>

            {isAnalyzing && (
              <p style={styles.centerText}>
                Trwa analiza obrazu przez sieć neuronową...
              </p>
            )}

            {apiError && <div style={styles.errorBox}>{apiError}</div>}

            {!isAnalyzing && predictions.length > 0 && (
              <div>
                <h3 style={styles.greenSubtitle}>Rozpoznane opcje:</h3>
                <div
                  style={{ display: "flex", flexDirection: "column", gap: 8 }}
                >
                  {predictions.map((pred, idx) => {
                    const rawName =
                      typeof pred === "string"
                        ? pred
                        : pred.class_name ||
                          pred.label ||
                          pred.product ||
                          pred.name ||
                          pred.class ||
                          "";
                    const plName = translateLabel(rawName);
                    const rawConf =
                      typeof pred === "object" && pred !== null
                        ? (pred.confidence ?? pred.probability ?? pred.score)
                        : undefined;
                    const conf =
                      rawConf !== undefined
                        ? (rawConf <= 1 ? rawConf * 100 : rawConf).toFixed(1)
                        : null;

                    return (
                      <div
                        key={idx}
                        style={{
                          ...styles.predCard,
                          borderColor: idx === 0 ? "#2e7d32" : "#cbd5e1",
                        }}
                      >
                        <div style={styles.predTop}>
                          <strong style={{ color: "#1e293b" }}>
                            {idx + 1}. {plName}
                          </strong>
                          {conf && (
                            <span
                              style={{
                                ...styles.confBadge,
                                backgroundColor:
                                  idx === 0 ? "#2e7d32" : "#64748b",
                              }}
                            >
                              {conf}%
                            </span>
                          )}
                        </div>
                        <button
                          type="button"
                          onClick={() => addToPantry(plName)}
                          style={styles.addSmallBtn}
                        >
                          + Dodaj do spiżarni
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {!isAnalyzing && predictions.length === 0 && !apiError && (
              <p style={styles.centerText}>
                Wgraj zdjęcie po lewej stronie i kliknij{" "}
                <strong>Rozpoznaj produkt</strong>.
              </p>
            )}

            <hr style={styles.divider} />

            <label style={styles.boldLabel}>
              Dodaj składnik ręcznie (jeśli brakuje na zdjęciu):
            </label>
            <form onSubmit={handleManualAdd} style={styles.manualForm}>
              <input
                type="text"
                placeholder="np. Mąka, Masło, Mleko, Jajka..."
                value={manualIngredient}
                onChange={(e) => setManualIngredient(e.target.value)}
                style={styles.input}
              />
              <button type="submit" style={styles.outlineGreenBtn}>
                Dodaj
              </button>
            </form>

            <div style={{ marginTop: 14 }}>
              <label style={styles.boldLabel}>
                Twoja wirtualna spiżarnia ({pantry.length}):
              </label>
              <div style={styles.pantryBox}>
                {pantry.length === 0 ? (
                  <span style={{ color: "#64748b", fontSize: 14 }}>
                    Spiżarnia jest pusta. Dodaj coś ze zdjęcia lub wpisz
                    ręcznie.
                  </span>
                ) : (
                  pantry.map((item) => (
                    <span key={item} style={styles.pantryChip}>
                      {item}
                      <button
                        type="button"
                        onClick={() => removeFromPantry(item)}
                        style={styles.chipClose}
                      >
                        ×
                      </button>
                    </span>
                  ))
                )}
              </div>
            </div>
          </section>
        </div>

        <div style={{ textAlign: "center", margin: "20px 0" }}>
          <button
            type="button"
            onClick={handleSearchRecipes}
            disabled={pantry.length === 0}
            style={{
              ...styles.searchBtn,
              opacity: pantry.length === 0 ? 0.6 : 1,
              cursor: pantry.length === 0 ? "not-allowed" : "pointer",
            }}
          >
            Szukaj przepisów z tych składników 🍽️
          </button>
          {pantry.length === 0 && (
            <p style={{ color: "#64748b", fontSize: 13, marginTop: 6 }}>
              Dodaj przynajmniej jeden składnik do spiżarni, aby wyszukać
              przepisy.
            </p>
          )}
        </div>

        {hasSearched && (
          <section style={{ marginTop: 24 }}>
            <h2 style={styles.resultsHeading}>
              3. Rekomendowane przepisy dla Ciebie ({recommendedRecipes.length})
            </h2>
            <p style={styles.resultsSub}>
              Posortowane według dopasowania składników (70%) oraz bliskości do
              celu {targetMealKcal} kcal (30%).
            </p>

            {recommendedRecipes.length === 0 ? (
              <div style={styles.card}>
                <p style={styles.centerText}>
                  Brak przepisów pasujących do wybranych składników i filtrów
                  diety. Spróbuj dodać inne produkty lub wyłączyć filtry.
                </p>
              </div>
            ) : (
              <div style={styles.recipesGrid}>
                {recommendedRecipes.map((recipe) => {
                  const rKey = recipe.id || recipe.title;
                  const isExpanded = expandedRecipeId === rKey;
                  const isLogged = justLoggedId === rKey;

                  return (
                    <div key={rKey} style={styles.recipeCard}>
                      <div style={styles.recipeTopBadges}>
                        <span style={styles.matchBadge}>
                          Dopasowanie: {recipe.matchPercent}%
                        </span>
                        <span style={styles.kcalBadge}>
                          🔥 {recipe.calories} kcal
                        </span>
                      </div>

                      <div style={styles.recipeEmoji}>{recipe.emoji}</div>
                      <h3 style={styles.recipeTitle}>{recipe.title}</h3>

                      <div style={styles.recipeMeta}>
                        <span>⏱ {recipe.prepTime}</span>
                        <span>📊 {recipe.difficulty}</span>
                        <span>
                          ✅ {recipe.matchedCount}/{recipe.totalCount} skł.
                        </span>
                      </div>

                      <div style={styles.macroLine}>
                        B: {recipe.protein}g | T: {recipe.fat}g | W:{" "}
                        {recipe.carbs}g
                      </div>

                      {recipe.missingIngredients.length > 0 && (
                        <div style={{ marginTop: 10 }}>
                          <div style={styles.missingLabel}>
                            Brakujące składniki:
                          </div>
                          <div style={styles.missingWrap}>
                            {recipe.missingIngredients.map((m) => (
                              <span key={m} style={styles.missingChip}>
                                {m}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {isExpanded && (
                        <div style={styles.expandedBox}>
                          <strong>Składniki:</strong>
                          <ul style={styles.ingList}>
                            {(recipe.ingredients || []).map((ing, i) => (
                              <li key={i}>
                                {typeof ing === "string"
                                  ? ing
                                  : `${ing.name} (${ing.amount})`}
                              </li>
                            ))}
                          </ul>
                          <strong>Przygotowanie:</strong>
                          {Array.isArray(recipe.instructions) ? (
                            <ol style={styles.stepsList}>
                              {recipe.instructions.map((step, i) => (
                                <li key={i}>{step}</li>
                              ))}
                            </ol>
                          ) : (
                            <p style={{ fontSize: 13, marginTop: 4 }}>
                              {recipe.instructions}
                            </p>
                          )}
                        </div>
                      )}

                      <div style={styles.recipeActions}>
                        <button
                          type="button"
                          onClick={() =>
                            setExpandedRecipeId(isExpanded ? null : rKey)
                          }
                          style={styles.outlineGreenBtnFull}
                        >
                          {isExpanded ? "Zwiń przepis" : "Zobacz pełny przepis"}
                        </button>
                        <button
                          type="button"
                          onClick={() => handleLogMeal(recipe)}
                          style={{
                            ...styles.eatBtn,
                            backgroundColor: isLogged ? "#15803d" : "#2e7d32",
                          }}
                        >
                          {isLogged
                            ? "✓ Zapisano w bilansie!"
                            : "+ Dodaj do bilansu"}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#f4f6f8",
    fontFamily: "'Segoe UI', Roboto, Arial, sans-serif",
    color: "#1e293b",
    colorScheme: "light",
    paddingBottom: 48,
  },
  header: {
    backgroundColor: "#2e7d32",
    color: "#fff",
    padding: "14px 24px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: 12,
  },
  headerTitle: {
    margin: 0,
    fontSize: 19,
    fontWeight: 700,
    color: "#fff",
  },
  settingsBtn: {
    backgroundColor: "transparent",
    color: "#fff",
    border: "1px solid rgba(255,255,255,0.75)",
    borderRadius: 6,
    padding: "6px 12px",
    cursor: "pointer",
    fontSize: 13,
  },
  container: {
    maxWidth: 1180,
    margin: "20px auto",
    padding: "0 16px",
  },
  card: {
    backgroundColor: "#ffffff",
    color: "#1e293b",
    borderRadius: 10,
    padding: 20,
    boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
    marginBottom: 18,
  },
  twoCol: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
    gap: 18,
  },
  profileGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(145px, 1fr))",
    gap: 12,
  },
  smallLabel: {
    display: "block",
    fontSize: 12,
    fontWeight: 600,
    color: "#475569",
    marginBottom: 4,
  },
  label: {
    display: "block",
    fontSize: 13,
    fontWeight: 600,
    color: "#1e293b",
    marginBottom: 6,
  },
  boldLabel: {
    display: "block",
    fontSize: 14,
    fontWeight: 700,
    color: "#1e293b",
    marginBottom: 6,
    textAlign: "center",
  },
  input: {
    width: "100%",
    boxSizing: "border-box",
    padding: "8px 10px",
    borderRadius: 6,
    border: "1px solid #cbd5e1",
    backgroundColor: "#ffffff",
    color: "#1e293b",
    fontSize: 14,
  },
  mealRow: {
    marginTop: 14,
    paddingTop: 12,
    borderTop: "1px solid #e2e8f0",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: 12,
  },
  mealButtonsWrap: {
    display: "flex",
    alignItems: "center",
    flexWrap: "wrap",
    gap: 8,
  },
  mealChip: {
    padding: "6px 11px",
    borderRadius: 20,
    border: "1px solid #cbd5e1",
    fontSize: 13,
    fontWeight: 600,
    cursor: "pointer",
  },
  dietToggles: {
    display: "flex",
    gap: 16,
    alignItems: "center",
  },
  checkboxLabel: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    fontSize: 14,
    fontWeight: 600,
    color: "#1e293b",
    cursor: "pointer",
  },
  dailyBox: {
    marginTop: 14,
    backgroundColor: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: 8,
    padding: 12,
  },
  dailyHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: 8,
    fontSize: 14,
  },
  progressTrack: {
    height: 10,
    backgroundColor: "#e2e8f0",
    borderRadius: 6,
    overflow: "hidden",
    margin: "8px 0",
  },
  progressFill: {
    height: "100%",
    transition: "width 0.3s ease",
  },
  targetInfo: {
    fontSize: 13,
    color: "#334155",
  },
  logToggleBtn: {
    backgroundColor: "#ffffff",
    color: "#1e293b",
    border: "1px solid #cbd5e1",
    borderRadius: 6,
    padding: "4px 10px",
    fontSize: 12,
    fontWeight: 600,
    cursor: "pointer",
  },
  logList: {
    marginTop: 10,
    paddingTop: 8,
    borderTop: "1px dashed #cbd5e1",
    display: "flex",
    flexDirection: "column",
    gap: 6,
  },
  logItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#ffffff",
    padding: "6px 10px",
    borderRadius: 6,
    border: "1px solid #e2e8f0",
    fontSize: 13,
  },
  removeLogBtn: {
    backgroundColor: "#fee2e2",
    color: "#dc2626",
    border: "none",
    borderRadius: 4,
    width: 22,
    height: 22,
    fontWeight: 700,
    cursor: "pointer",
  },
  cardTitle: {
    margin: "0 0 12px 0",
    fontSize: 17,
    fontWeight: 700,
    color: "#1e293b",
    textAlign: "center",
  },
  cardHeaderRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  fileBadge: {
    fontSize: 12,
    backgroundColor: "#f1f5f9",
    padding: "3px 8px",
    borderRadius: 6,
    color: "#475569",
  },
  hint: {
    textAlign: "center",
    fontSize: 13,
    color: "#475569",
    marginBottom: 12,
  },
  fileInput: {
    width: "100%",
    padding: 8,
    border: "1px solid #cbd5e1",
    borderRadius: 6,
    backgroundColor: "#ffffff",
    color: "#1e293b",
    boxSizing: "border-box",
  },
  previewBox: {
    margin: "14px auto",
    width: 220,
    height: 220,
    border: "1px dashed #94a3b8",
    borderRadius: 8,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
    backgroundColor: "#ffffff",
  },
  previewImg: {
    maxWidth: "100%",
    maxHeight: "100%",
    objectFit: "contain",
  },
  primaryBtn: {
    width: "100%",
    marginTop: 14,
    padding: "12px",
    backgroundColor: "#2e7d32",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    fontSize: 15,
    fontWeight: 700,
  },
  greenSubtitle: {
    color: "#2e7d32",
    textAlign: "center",
    fontSize: 15,
    margin: "6px 0 10px 0",
  },
  predCard: {
    border: "1.5px solid #cbd5e1",
    borderRadius: 8,
    padding: 10,
    backgroundColor: "#ffffff",
  },
  predTop: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  confBadge: {
    color: "#fff",
    fontSize: 12,
    fontWeight: 700,
    padding: "2px 8px",
    borderRadius: 12,
  },
  addSmallBtn: {
    width: "100%",
    backgroundColor: "#f8fafc",
    border: "1px solid #cbd5e1",
    borderRadius: 6,
    padding: "5px",
    color: "#2e7d32",
    fontWeight: 600,
    fontSize: 13,
    cursor: "pointer",
  },
  centerText: {
    textAlign: "center",
    color: "#64748b",
    fontSize: 14,
    margin: "24px 0",
  },
  errorBox: {
    backgroundColor: "#fef2f2",
    border: "1px solid #fecaca",
    color: "#b91c1c",
    padding: 10,
    borderRadius: 6,
    fontSize: 13,
    marginBottom: 10,
  },
  divider: {
    border: "none",
    borderTop: "1px solid #e2e8f0",
    margin: "16px 0",
  },
  manualForm: {
    display: "flex",
    gap: 8,
  },
  outlineGreenBtn: {
    backgroundColor: "#ffffff",
    color: "#2e7d32",
    border: "1px solid #2e7d32",
    borderRadius: 6,
    padding: "0 14px",
    fontWeight: 600,
    cursor: "pointer",
  },
  pantryBox: {
    minHeight: 46,
    backgroundColor: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: 8,
    padding: 10,
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
    alignItems: "center",
    justifyContent: "center",
  },
  pantryChip: {
    backgroundColor: "#2e7d32",
    color: "#fff",
    padding: "5px 10px",
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 600,
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
  },
  chipClose: {
    background: "none",
    border: "none",
    color: "#fff",
    fontWeight: 700,
    cursor: "pointer",
    padding: 0,
    fontSize: 15,
  },
  searchBtn: {
    backgroundColor: "#f3c64f",
    color: "#1e293b",
    border: "none",
    borderRadius: 8,
    padding: "14px 36px",
    fontSize: 16,
    fontWeight: 700,
    boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
  },
  resultsHeading: {
    textAlign: "center",
    color: "#2e7d32",
    margin: "0 0 4px 0",
  },
  resultsSub: {
    textAlign: "center",
    color: "#475569",
    fontSize: 13,
    margin: "0 0 18px 0",
  },
  recipesGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(310px, 1fr))",
    gap: 18,
  },
  recipeCard: {
    backgroundColor: "#ffffff",
    color: "#1e293b",
    borderRadius: 10,
    padding: 18,
    boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
  },
  recipeTopBadges: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  matchBadge: {
    backgroundColor: "#2563eb",
    color: "#fff",
    fontSize: 12,
    fontWeight: 700,
    padding: "3px 9px",
    borderRadius: 12,
  },
  kcalBadge: {
    backgroundColor: "#f1f5f9",
    color: "#334155",
    fontSize: 12,
    fontWeight: 700,
    padding: "3px 9px",
    borderRadius: 12,
  },
  recipeEmoji: {
    fontSize: 44,
    textAlign: "center",
    margin: "12px 0 6px 0",
  },
  recipeTitle: {
    textAlign: "center",
    fontSize: 17,
    color: "#1e293b",
    margin: "0 0 8px 0",
  },
  recipeMeta: {
    display: "flex",
    justifyContent: "center",
    gap: 12,
    fontSize: 12,
    color: "#475569",
  },
  macroLine: {
    textAlign: "center",
    fontSize: 12,
    color: "#64748b",
    marginTop: 4,
  },
  missingLabel: {
    textAlign: "center",
    fontSize: 12,
    fontWeight: 700,
    color: "#b91c1c",
    marginBottom: 6,
  },
  missingWrap: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "center",
    gap: 6,
  },
  missingChip: {
    border: "1px solid #fca5a5",
    color: "#b91c1c",
    borderRadius: 12,
    padding: "2px 8px",
    fontSize: 11,
  },
  expandedBox: {
    marginTop: 12,
    padding: 10,
    backgroundColor: "#f8fafc",
    color: "#1e293b",
    borderRadius: 8,
    fontSize: 13,
    textAlign: "left",
  },
  ingList: {
    margin: "4px 0 8px 18px",
    padding: 0,
  },
  stepsList: {
    margin: "4px 0 0 18px",
    padding: 0,
  },
  recipeActions: {
    marginTop: 14,
    display: "flex",
    flexDirection: "column",
    gap: 8,
  },
  outlineGreenBtnFull: {
    width: "100%",
    backgroundColor: "#ffffff",
    color: "#2e7d32",
    border: "1px solid #2e7d32",
    borderRadius: 6,
    padding: "8px",
    fontWeight: 600,
    cursor: "pointer",
  },
  eatBtn: {
    width: "100%",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "9px",
    fontWeight: 700,
    cursor: "pointer",
  },
};
