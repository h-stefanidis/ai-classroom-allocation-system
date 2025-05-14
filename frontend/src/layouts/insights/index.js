// src/layouts/insights/index.js

import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";

const academicPerformance = {
  labels: ["Class 1", "Class 2", "Class 3", "Class 4"],
  datasets: {
    label: "Average Academic %",
    data: [75, 80, 72, 58],
  },
};

const wellbeingTrend = {
  labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
  datasets: {
    label: "Social Wellbeing %",
    data: [85, 78, 73, 69],
  },
};

function Insights() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        {/* Top Metrics */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={3}>
            <ComplexStatisticsCard
              icon="groups"
              title="Total Students"
              count={124}
              percentage={{ color: "info", label: "across all classrooms" }}
            />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <ComplexStatisticsCard
              icon="school"
              title="Classrooms"
              count={4}
              percentage={{ color: "info", label: "currently configured" }}
            />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <ComplexStatisticsCard
              icon="sentiment_very_dissatisfied"
              color="error"
              title="Avg Wellbeing"
              count="62%"
              percentage={{ color: "error", label: "at-risk emotional trend" }}
            />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <ComplexStatisticsCard
              icon="trending_up"
              color="success"
              title="Avg Academic"
              count="78%"
              percentage={{ color: "success", label: "steady improvement" }}
            />
          </Grid>
        </Grid>

        {/* Charts Section */}
        <MDBox mt={10}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <ReportsBarChart
                color="primary"
                title="Academic Performance by Class"
                description="Some classes are performing below target"
                date="updated 2 mins ago"
                chart={academicPerformance}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <ReportsLineChart
                color="success"
                title="Social Wellbeing Over Time"
                description="Trend of student cohesion and stability"
                date="updated just now"
                chart={wellbeingTrend}
              />
            </Grid>
          </Grid>
        </MDBox>

        {/* Justification Section */}
        <MDBox mt={6}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h5" fontWeight="medium" gutterBottom>
              AI Allocation Justification
            </MDTypography>
            <MDBox mt={2}>
              <MDTypography variant="body2" color="text">
                Classroom 2 was optimized to balance academic performance with emotional wellbeing.
                High-performing students with positive social connections were grouped together,
                while past instances of disrespect were minimized by reassigning students based on
                behavioral history. Further tuning is suggested for Classroom 3 due to low academic
                cohesion.
              </MDTypography>
            </MDBox>
          </Card>
        </MDBox>
      </MDBox>
    </DashboardLayout>
  );
}

export default Insights;
