import React from "react";
import LayoutWrapper from "components/LayoutWrapper";
import MDTypography from "components/MDTypography";

const OnboardingPage = () => {
  return (
    <LayoutWrapper>
      <MDTypography variant="h4" mb={2}>
        Welcome to ClassForge!
      </MDTypography>
      <MDTypography variant="body1">
        This onboarding page will guide new users through submitting preferences, viewing schedules,
        and understanding key features.
      </MDTypography>
    </LayoutWrapper>
  );
};

export default OnboardingPage;
