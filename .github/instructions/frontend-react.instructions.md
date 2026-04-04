---
description: "Use when writing or editing React/TypeScript frontend code: components, pages, hooks, stores, API functions."
applyTo: "frontend/src/**/*.{ts,tsx}"
---
# Frontend TypeScript/React Conventions

## Data Fetching
- Page-level: `useCachedData<T>(cacheKey, fetcher, { enabled })`. Always include `currency` in cache keys for monetary data.
- Global sync: stores are synced via `usePortfolioSync()` in `MainLayout`.

## Currency
- Use `useCurrency()` hook for formatting: `const { currency, format, symbol, locale } = useCurrency()`.
- Always pass `currency` as API query param for endpoints that return monetary values.
- Never hardcode `R$`, `US$`, or `pt-BR`/`en-US` — derive from the hook.

## State Management
- Zustand stores are thin: state + setters only.
- API functions in `src/api/` are pure (return data, no store mutations).
- Actions in `src/actions/` bridge API → Zustand stores with caching.

## Components
- Naming: `{Feature}Form.tsx`, `{Feature}Table.tsx`, `{Feature}Chart.tsx`.
- Use atomic UI components from `components/ui/` (`AppTable`, `AppCard`, `AppPieChart`, `AppBarChart`).
- MUI for layout and theming. Access theme via `useTheme()`.

## TypeScript
- Strict mode enabled. Define interfaces in `src/types/`.
- Prefer explicit types. `any` is tolerated but discouraged.

## Color and Themes
- Always use colors derived from the theme via useTheme().
Never hardcode colors (hex, rgb, or named colors like "red", "green").
- If a new color is needed, align first to add it to the global theme (avoid one-off local colors).