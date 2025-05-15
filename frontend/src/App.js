import { useState, useEffect, useMemo } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";

// @mui
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

// Components
import MDBox from "./components/MDBox";
import Sidenav from "./examples/Sidenav";

// Themes
import theme from "./assets/theme";
import themeRTL from "./assets/theme/theme-rtl";
import themeDark from "./assets/theme-dark";
import themeDarkRTL from "./assets/theme-dark/theme-rtl";

// RTL
import rtlPlugin from "stylis-plugin-rtl";
import { CacheProvider } from "@emotion/react";
import createCache from "@emotion/cache";

// Routes
import routes from "./routes";
import PrivateRoute from "./routes/PrivateRoute";

// Context
import { useMaterialUIController, setMiniSidenav, setOpenConfigurator } from "./context";

// Logos
import brandLogo from "./assets/images/sna-logo.png";

export default function App() {
  const [controller, dispatch] = useMaterialUIController();
  const {
    miniSidenav,
    direction,
    layout,
    openConfigurator,
    sidenavColor,
    transparentSidenav,
    whiteSidenav,
    darkMode,
  } = controller;

  const [onMouseEnter, setOnMouseEnter] = useState(false);
  const [rtlCache, setRtlCache] = useState(null);
  const { pathname } = useLocation();

  // Set RTL cache
  useMemo(() => {
    const cacheRtl = createCache({
      key: "rtl",
      stylisPlugins: [rtlPlugin],
    });
    setRtlCache(cacheRtl);
  }, []);

  const handleOnMouseEnter = () => {
    if (miniSidenav && !onMouseEnter) {
      setMiniSidenav(dispatch, false);
      setOnMouseEnter(true);
    }
  };

  const handleOnMouseLeave = () => {
    if (onMouseEnter) {
      setMiniSidenav(dispatch, true);
      setOnMouseEnter(false);
    }
  };

  const handleConfiguratorOpen = () => setOpenConfigurator(dispatch, !openConfigurator);

  // Set text direction
  useEffect(() => {
    document.body.setAttribute("dir", direction);
  }, [direction]);

  // Scroll to top on route change
  useEffect(() => {
    document.documentElement.scrollTop = 0;
    document.scrollingElement.scrollTop = 0;
  }, [pathname]);

  // Build routes with auth check
  const getRoutes = (allRoutes) =>
    allRoutes.map((route) => {
      if (route.collapse) return getRoutes(route.collapse);
      if (route.route) {
        const isAuthPage = route.route.startsWith("/authentication");
        return (
          <Route
            exact
            path={route.route}
            element={isAuthPage ? route.component : <PrivateRoute>{route.component}</PrivateRoute>}
            key={route.key}
          />
        );
      }
      return null;
    });

  // RTL layout
  if (direction === "rtl") {
    return (
      <CacheProvider value={rtlCache}>
        <ThemeProvider theme={darkMode ? themeDarkRTL : themeRTL}>
          <CssBaseline />
          {layout === "dashboard" && (
            <Sidenav
              color={sidenavColor}
              brand={brandLogo}
              brandName="ClassForge"
              routes={routes}
              onMouseEnter={handleOnMouseEnter}
              onMouseLeave={handleOnMouseLeave}
            />
          )}
          <Routes>
            {getRoutes(routes)}
            <Route path="*" element={<Navigate to="/authentication/sign-in" replace />} />
          </Routes>
        </ThemeProvider>
      </CacheProvider>
    );
  }

  // LTR layout
  return (
    <ThemeProvider theme={darkMode ? themeDark : theme}>
      <CssBaseline />
      {layout === "dashboard" && (
        <Sidenav
          color={sidenavColor}
          brand={brandLogo}
          brandName="ClassForge"
          routes={routes}
          onMouseEnter={handleOnMouseEnter}
          onMouseLeave={handleOnMouseLeave}
        />
      )}
      <Routes>
        {getRoutes(routes)}
        <Route path="*" element={<Navigate to="/authentication/sign-in" replace />} />
      </Routes>
    </ThemeProvider>
  );
}
