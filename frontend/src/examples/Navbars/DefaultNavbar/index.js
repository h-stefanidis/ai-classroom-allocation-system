import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import PropTypes from "prop-types";

// MUI components
import Container from "@mui/material/Container";

// Material Dashboard 2 components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Theme & context
import { useMaterialUIController } from "context";

function DefaultNavbar({ transparent, light, action }) {
  const [controller] = useMaterialUIController();
  const { darkMode } = controller;

  useEffect(() => {
    const displayMobileNavbar = () => {
      // Add logic for displaying the mobile navbar
    };

    window.addEventListener("resize", displayMobileNavbar);
    displayMobileNavbar();
    return () => window.removeEventListener("resize", displayMobileNavbar);
  }, []);

  return (
    <Container>
      <MDBox
        py={2.5}
        px={{ xs: 4, sm: transparent ? 2 : 3, lg: transparent ? 0 : 2 }}
        my={3}
        width="66%"
        borderRadius="lg"
        shadow={transparent ? "none" : "md"}
        color={light ? "white" : "dark"}
        display="flex"
        justifyContent="center"
        alignItems="center"
        position="absolute"
        left="50%"
        zIndex={3}
        sx={({
          palette: { transparent: transparentColor, white, background },
          functions: { rgba },
        }) => ({
          backgroundColor: transparent
            ? transparentColor.main
            : rgba(darkMode ? background.sidenav : white.main, 0.8),
          backdropFilter: transparent ? "none" : `saturate(200%) blur(30px)`,
          transform: "translateX(-50%)",
        })}
      >
        <MDBox py={transparent ? 1.5 : 0.75} lineHeight={1} display="flex" justifyContent="center">
          <MDTypography
            fontWeight="bold"
            color={light ? "white" : "dark"}
            align="center"
            variant="h4"
          >
            ClassForge – An AI-Assisted Student Allocation System
          </MDTypography>
        </MDBox>
      </MDBox>
    </Container>
  );
}

DefaultNavbar.defaultProps = {
  transparent: false,
  light: false,
  action: false,
};

DefaultNavbar.propTypes = {
  transparent: PropTypes.bool,
  light: PropTypes.bool,
  action: PropTypes.oneOfType([
    PropTypes.bool,
    PropTypes.shape({
      type: PropTypes.oneOf(["external", "internal"]).isRequired,
      route: PropTypes.string.isRequired,
      color: PropTypes.oneOf([
        "primary",
        "secondary",
        "info",
        "success",
        "warning",
        "error",
        "dark",
        "light",
      ]),
      label: PropTypes.string.isRequired,
    }),
  ]),
};

export default DefaultNavbar;
