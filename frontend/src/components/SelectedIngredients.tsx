interface SelectedIngredientsProps {
  ingredients: string[];
  onRemove: (name: string) => void;
}

function SelectedIngredients({
  ingredients,
  onRemove,
}: SelectedIngredientsProps) {
  return (
    <div className="mt-2">
      {ingredients.length === 0 ? (
        <span className="text-muted small">Brak dodanych składników</span>
      ) : (
        ingredients.map((item) => (
          <span key={item} className="badge bg-success me-1 mb-1 p-2">
            {item}

            <button
              type="button"
              className="ingredient-remove"
              aria-label={`Usuń ${item}`}
              onClick={() => onRemove(item)}
            >
              ×
            </button>
          </span>
        ))
      )}
    </div>
  );
}

export default SelectedIngredients;
