import { useState, useEffect } from "react";
import { useLocation, Link, useNavigate } from "react-router-dom";
import PropTypes from "prop-types";

import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import Icon from "@mui/material/Icon";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";

import Fuse from "fuse.js";

import MDBox from "components/MDBox";
import Breadcrumbs from "examples/Breadcrumbs";
import NotificationItem from "examples/Items/NotificationItem";

import {
  navbar,
  navbarContainer,
  navbarRow,
  navbarIconButton,
  navbarMobileMenu,
} from "examples/Navbars/DashboardNavbar/styles";

import { useMaterialUIController, setTransparentNavbar, setMiniSidenav } from "context";

function DashboardNavbar({ absolute, light, isMini }) {
  const [navbarType, setNavbarType] = useState();
  const [controller, dispatch] = useMaterialUIController();
  const { miniSidenav, transparentNavbar, fixedNavbar, darkMode } = controller;
  const [openSettingsMenu, setOpenSettingsMenu] = useState(null);
  const [searchValue, setSearchValue] = useState("");
  const [suggestions, setSuggestions] = useState([]);

  const navigate = useNavigate();
  const route = useLocation().pathname.split("/").slice(1);

  const searchableRoutes = [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Insights", path: "/insights" },
    { label: "Classroom Allocator", path: "/dashboard/tables" },
    { label: "Visualization", path: "/dashboard/visualization" },
    { label: "Upload Data", path: "/upload-data" },
    { label: "Onboarding", path: "/onboarding" },
    { label: "Preferences", path: "/preferences" },
    { label: "Feedback", path: "/feedback" },
    { label: "Admin Tools", path: "/admin-tools" },
    { label: "Profile", path: "/profile" },
  ];

  const fuse = new Fuse(searchableRoutes, {
    keys: ["label"],
    threshold: 0.4,
  });

  useEffect(() => {
    setNavbarType(fixedNavbar ? "sticky" : "static");
    const handleTransparentNavbar = () => {
      setTransparentNavbar(dispatch, (fixedNavbar && window.scrollY === 0) || !fixedNavbar);
    };
    window.addEventListener("scroll", handleTransparentNavbar);
    handleTransparentNavbar();
    return () => window.removeEventListener("scroll", handleTransparentNavbar);
  }, [dispatch, fixedNavbar]);

  useEffect(() => {
    setSuggestions(searchableRoutes);
  }, []);

  const handleMiniSidenav = () => setMiniSidenav(dispatch, !miniSidenav);
  const handleOpenSettingsMenu = (event) => setOpenSettingsMenu(event.currentTarget);
  const handleCloseSettingsMenu = () => setOpenSettingsMenu(null);

  const renderSettingsMenu = () => (
    <Menu
      anchorEl={openSettingsMenu}
      open={Boolean(openSettingsMenu)}
      onClose={handleCloseSettingsMenu}
      anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
      sx={{ mt: 2 }}
    >
      <Link to="/authentication/sign-in" style={{ textDecoration: "none", color: "inherit" }}>
        <NotificationItem icon={<Icon>logout</Icon>} title="Sign out" />
      </Link>
    </Menu>
  );

  const iconsStyle = ({ palette: { dark, white, text }, functions: { rgba } }) => ({
    color: light || darkMode ? white.main : dark.main,
    ...(transparentNavbar &&
      !light && {
        color: darkMode ? rgba(text.main, 0.6) : text.main,
      }),
  });

  return (
    <AppBar
      position={absolute ? "absolute" : navbarType}
      color="inherit"
      sx={(theme) => navbar(theme, { transparentNavbar, absolute, light, darkMode })}
    >
      <Toolbar sx={(theme) => navbarContainer(theme)}>
        <MDBox color="inherit" mb={{ xs: 1, md: 0 }} sx={(theme) => navbarRow(theme, { isMini })}>
          <Breadcrumbs icon="home" title={route[route.length - 1]} route={route} light={light} />
        </MDBox>
        {!isMini && (
          <MDBox sx={(theme) => navbarRow(theme, { isMini })}>
            {/* 🔍 Fuzzy Autocomplete Search */}
            <MDBox pr={1} sx={{ minWidth: 250 }}>
              <Autocomplete
                freeSolo
                disableClearable
                options={suggestions}
                getOptionLabel={(option) => option.label}
                inputValue={searchValue}
                onInputChange={(e, value) => {
                  setSearchValue(value);
                  const results = fuse.search(value).map((r) => r.item);
                  setSuggestions(value ? results : searchableRoutes);
                }}
                onChange={(e, newValue) => {
                  if (newValue?.path) {
                    navigate(newValue.path);
                    setSearchValue(""); // Optional reset
                  }
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Search"
                    variant="outlined"
                    size="small"
                    InputProps={{ ...params.InputProps, type: "search" }}
                  />
                )}
              />
            </MDBox>

            <MDBox color={light ? "white" : "inherit"}>
              {/* 👤 Profile Button */}
              <Link to="/profile">
                <IconButton sx={navbarIconButton} size="small" disableRipple>
                  <Icon sx={iconsStyle}>account_circle</Icon>
                </IconButton>
              </Link>

              {/* 📂 Mini Sidenav Toggle */}
              <IconButton
                size="small"
                disableRipple
                sx={navbarMobileMenu}
                onClick={handleMiniSidenav}
              >
                <Icon sx={iconsStyle} fontSize="medium">
                  {miniSidenav ? "menu_open" : "menu"}
                </Icon>
              </IconButton>

              {/* ⚙️ Settings Dropdown */}
              <IconButton
                size="small"
                disableRipple
                color="inherit"
                sx={navbarIconButton}
                onClick={handleOpenSettingsMenu}
              >
                <Icon sx={iconsStyle}>settings</Icon>
              </IconButton>
              {renderSettingsMenu()}

              {/* 🔔 Notification Icon (Static) */}
              <IconButton size="small" disableRipple color="inherit" sx={navbarIconButton}>
                <Icon sx={iconsStyle}>notifications</Icon>
              </IconButton>
            </MDBox>
          </MDBox>
        )}
      </Toolbar>
    </AppBar>
  );
}

DashboardNavbar.defaultProps = {
  absolute: false,
  light: false,
  isMini: false,
};

DashboardNavbar.propTypes = {
  absolute: PropTypes.bool,
  light: PropTypes.bool,
  isMini: PropTypes.bool,
};

export default DashboardNavbar;
