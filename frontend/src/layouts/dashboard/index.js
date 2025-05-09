// src/layouts/dashboard/index.jsx

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import VisualizationSection from "components/VisualizationSection";

export default function Dashboard() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        {/* 🔹 Summary Cards */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={6}>
            <ComplexStatisticsCard
              icon="track_changes"
              title="Allocations Processed"
              count="12"
              percentage={{ color: "success", label: "last 24 hours" }}
            />
          </Grid>
          <Grid item xs={12} md={6} lg={6}>
            <ComplexStatisticsCard
              icon="hub"
              title="Visualization Active"
              count="5 Networks"
              percentage={{ color: "info", label: "updated live" }}
            />
          </Grid>
        </Grid>

        {/* 📊 Allocation Visualization */}
        <MDBox mt={4}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h5" fontWeight="medium" gutterBottom>
              Classroom Allocation Network
            </MDTypography>
            <VisualizationSection />
          </Card>
        </MDBox>

        {/* 📘 AI Justification Summary */}
        <MDBox mt={4}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h5" fontWeight="medium" gutterBottom>
              AI Allocation Justification
            </MDTypography>
            <MDTypography variant="body2" color="text">
              This visualization shows optimized classroom groupings based on academic performance,
              social bonding, and wellbeing metrics. Students were clustered to improve retention
              and reduce negative interaction patterns. Adjustments are ongoing as new data is
              processed.
            </MDTypography>
          </Card>
        </MDBox>
      </MDBox>
    </DashboardLayout>
  );
}
