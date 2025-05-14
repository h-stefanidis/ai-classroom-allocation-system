import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import VisualizationSection from "components/VisualizationSection";

// Charts
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// Dummy chart data (overview trend)
const chartData = [
  { name: "Week 1", students: 40 },
  { name: "Week 2", students: 45 },
  { name: "Week 3", students: 50 },
  { name: "Week 4", students: 47 },
  { name: "Week 5", students: 53 },
];

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

        {/* 📈 Overview Line Chart */}
        <MDBox mt={4}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h5" fontWeight="medium" gutterBottom>
              Weekly Student Allocation Trend
            </MDTypography>
            <MDBox mt={3} height={300}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="students"
                    stroke="#1976d2"
                    strokeWidth={2}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </MDBox>
          </Card>
        </MDBox>

        {/* 🧠 Allocation Visualization */}
        <MDBox mt={4}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h5" fontWeight="medium" gutterBottom>
              Classroom Allocation Network
            </MDTypography>
            <MDBox
              sx={{
                overflowX: "auto",
                maxWidth: "100%",
                border: "1px solid #e0e0e0",
                borderRadius: "8px",
                p: 2,
                mt: 2,
              }}
            >
              <VisualizationSection />
            </MDBox>
          </Card>
        </MDBox>

        {/* 📘 Justification Section */}
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
