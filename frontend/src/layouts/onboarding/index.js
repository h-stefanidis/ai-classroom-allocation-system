import React from "react";

// Material Dashboard 2 components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";

// Custom MD2 components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";

// Layout wrappers
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";

function OnboardingPage() {
  return (
    <DashboardLayout>
      <DashboardNavbar />

      <MDBox py={3}>
        <MDBox mb={3}>
          <MDTypography variant="h4" fontWeight="bold">
            👋 Welcome to ClassForge
          </MDTypography>
          <MDTypography variant="body2" color="text" mt={1}>
            ClassForge is an AI-powered classroom allocation system that helps educators form
            balanced, socially cohesive, and academically optimized classrooms.
          </MDTypography>
        </MDBox>

        <Grid container spacing={3}>
          {/* Step 1 - Upload Data */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3 }}>
              <MDTypography variant="h6" gutterBottom>
                1. Upload Student Data
              </MDTypography>
              <MDTypography variant="body2" color="text">
                Begin by uploading student survey and enrollment data. This data is used to build
                social and academic relationship graphs for optimal grouping.
              </MDTypography>
              <MDBox mt={2}>
                <MDButton
                  variant="contained"
                  color="info"
                  href="/upload-data"
                  startIcon={<Icon>upload</Icon>}
                >
                  Upload Data
                </MDButton>
              </MDBox>
            </Card>
          </Grid>

          {/* Step 2 - Set Preferences */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3 }}>
              <MDTypography variant="h6" gutterBottom>
                2. Configure AI Preferences
              </MDTypography>
              <MDTypography variant="body2" color="text">
                Select the number of classrooms and choose an AI model (e.g., GraphSAGE or
                Ensemble). These preferences will guide how students are allocated.
              </MDTypography>
              <MDBox mt={2}>
                <MDButton
                  variant="outlined"
                  color="info"
                  href="/preferences"
                  startIcon={<Icon>tune</Icon>}
                >
                  Set Preferences
                </MDButton>
              </MDBox>
            </Card>
          </Grid>

          {/* Step 3 - Allocate Students */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3 }}>
              <MDTypography variant="h6" gutterBottom>
                3. Generate Student Allocations
              </MDTypography>
              <MDTypography variant="body2" color="text">
                Run the allocation engine. The system will automatically create classroom groupings
                that optimize for academic performance, wellbeing, and peer relationships.
              </MDTypography>
              <MDBox mt={2}>
                <MDButton
                  variant="contained"
                  color="success"
                  href="/allocation"
                  startIcon={<Icon>groups</Icon>}
                >
                  Run Allocation
                </MDButton>
              </MDBox>
            </Card>
          </Grid>

          {/* Step 4 - View Insights */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3 }}>
              <MDTypography variant="h6" gutterBottom>
                4. Visualise Allocation Insights
              </MDTypography>
              <MDTypography variant="body2" color="text">
                Explore graphs that show class-level metrics, including academic scores, social
                wellbeing, and preserved friendships. Understand how each class is formed.
              </MDTypography>
              <MDBox mt={2}>
                <MDButton
                  variant="outlined"
                  color="info"
                  href="/insights"
                  startIcon={<Icon>bar_chart</Icon>}
                >
                  View Insights
                </MDButton>
              </MDBox>
            </Card>
          </Grid>

          {/* Optional - Help */}
          <Grid item xs={12}>
            <Card sx={{ p: 3 }}>
              <MDTypography variant="h6" gutterBottom>
                Need Help?
              </MDTypography>
              <MDTypography variant="body2" color="text">
                If you are unsure how to use any part of the system, contact your administrator or
                check the user guide.
              </MDTypography>
              <MDBox mt={2}>
                <MDButton variant="text" color="secondary" startIcon={<Icon>help_outline</Icon>}>
                  Contact Support
                </MDButton>
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
    </DashboardLayout>
  );
}

export default OnboardingPage;
