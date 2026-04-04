// src/theme/index.tsx
import { getCustomThemeById } from "@/stores/custom-themes";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import 'dayjs/locale/pt-br';
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import {
    darkThemes,
    DEFAULT_DARK_THEME_ID,
    DEFAULT_LIGHT_THEME_ID,
    getThemeById,
    lightThemes,
} from "./themes";

type ThemeMode = "light" | "dark";

type Ctx = {
  mode: ThemeMode;
  toggleTheme: () => void;
  lightThemeId: string;
  darkThemeId: string;
  setLightTheme: (id: string) => void;
  setDarkTheme: (id: string) => void;
};

export const ThemeModeContext = createContext<Ctx>({
  mode: "dark",
  toggleTheme: () => {},
  lightThemeId: DEFAULT_LIGHT_THEME_ID,
  darkThemeId: DEFAULT_DARK_THEME_ID,
  setLightTheme: () => {},
  setDarkTheme: () => {},
});

export const useThemeMode = () => useContext(ThemeModeContext);

export function ThemeRegistry({ children }: { children: React.ReactNode }) {
  const getInitialMode = (): ThemeMode => {
    const saved = localStorage.getItem("theme-mode") as ThemeMode | null;
    if (saved === "light" || saved === "dark") return saved;

    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
      return "light";
    }

    return "dark";
  };

  const [mode, setMode] = useState<ThemeMode>(() => getInitialMode());

  const [lightThemeId, setLightThemeIdState] = useState<string>(
    () => localStorage.getItem("theme-light-id") || DEFAULT_LIGHT_THEME_ID,
  );

  const [darkThemeId, setDarkThemeIdState] = useState<string>(
    () => localStorage.getItem("theme-dark-id") || DEFAULT_DARK_THEME_ID,
  );

  const toggleTheme = () => {
    setMode((prev) => {
      const next = prev === "light" ? "dark" : "light";
      localStorage.setItem("theme-mode", next);
      return next;
    });
  };

  const setLightTheme = (id: string) => {
    setLightThemeIdState(id);
    localStorage.setItem("theme-light-id", id);
    setMode("light");
    localStorage.setItem("theme-mode", "light");
  };

  const setDarkTheme = (id: string) => {
    setDarkThemeIdState(id);
    localStorage.setItem("theme-dark-id", id);
    setMode("dark");
    localStorage.setItem("theme-mode", "dark");
  };

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = () => {
      const saved = localStorage.getItem("theme-mode");
      if (!saved) setMode(media.matches ? "dark" : "light");
    };
    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, []);

  const theme = useMemo(() => {
    const id = mode === "light" ? lightThemeId : darkThemeId;
    const def = getThemeById(id) ?? getCustomThemeById(id);
    if (def) return def.theme;
    return mode === "light" ? lightThemes[0].theme : darkThemes[0].theme;
  }, [mode, lightThemeId, darkThemeId]);

  const ctx = useMemo<Ctx>(
    () => ({ mode, toggleTheme, lightThemeId, darkThemeId, setLightTheme, setDarkTheme }),
    [mode, lightThemeId, darkThemeId],
  );

  return (
    <ThemeModeContext.Provider value={ctx}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="pt-br">
          {children}
        </LocalizationProvider>
      </ThemeProvider>
    </ThemeModeContext.Provider>
  );
}
