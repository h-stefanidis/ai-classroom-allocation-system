import React from "react";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Custom Sections
import OverviewSection from "components/OverviewSection";
import VisualizationSection from "components/VisualizationSection";
import ScheduleSection from "components/ScheduleSection";

function Dashboard() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          {/* Overview Section */}
          <Grid item xs={12}>
            <OverviewSection />
          </Grid>

          {/* Visualization Section */}
          <Grid item xs={12}>
            <VisualizationSection />
          </Grid>

          {/* Schedule Section */}
          <Grid item xs={12}>
            <ScheduleSection />
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Dashboard;
