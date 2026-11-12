import translations from "../locales/pl.json";

export function translateProductName(rawName: string): string {
  const cleanKey = rawName.toLowerCase().replace(/^custom_/, "");

  return translations[cleanKey as keyof typeof translations] ?? `${rawName}`;
}

export function getConfidence(item: {
  confidence?: number;
  probability?: number;
  score?: number;
}): number {
  const value = Number(item.confidence ?? item.probability ?? item.score ?? 0);

  if (!Number.isFinite(value)) return 0;

  return Math.min(100, Math.max(0, value <= 1 ? value * 100 : value));
}
