import { useState } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import InputLabel from "@mui/material/InputLabel";
import FormControl from "@mui/material/FormControl";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";

const metrics = [
  "Academic",
  "Wellbeing",
  "Behavior",
  "Engagement",
  "Stability",
  "Friendship Bonds",
];

const randomStats = [60, 65, 50, 58, 52, 48];

const modelOptions = {
  "Model A": [75, 72, 65, 74, 70, 68],
  "Model B": [73, 70, 62, 72, 69, 66],
  "Model C": [78, 76, 70, 82, 75, 71],
};

export default function Comparison() {
  const [selectedModel, setSelectedModel] = useState("Model A");
  const modelStats = modelOptions[selectedModel];

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <MDTypography variant="h5" fontWeight="bold">
              Comparison
            </MDTypography>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl size="small" sx={{ minWidth: 200, float: "right" }}>
              <InputLabel>Select Model</InputLabel>
              <Select
                value={selectedModel}
                label="Select Model"
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                {Object.keys(modelOptions).map((model) => (
                  <MenuItem key={model} value={model}>
                    {model}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Metric Cards */}
        <Grid container spacing={3} mt={3}>
          {/* Random Allocation Metrics */}
          <Grid item xs={12} md={6}>
            <MDTypography variant="h6" mb={4}>
              Random Allocation Metrics
            </MDTypography>
            <Grid container spacing={2}>
              {metrics.map((metric, i) => (
                <Grid item xs={12} sm={6} md={6} key={`random-${metric}`}>
                  <ComplexStatisticsCard
                    icon="shuffle"
                    title={metric}
                    count={`${randomStats[i]}%`}
                    percentage={{ color: "error", label: "random strategy" }}
                  />
                </Grid>
              ))}
            </Grid>
          </Grid>

          {/* Selected Model Metrics */}
          <Grid item xs={12} md={6}>
            <MDTypography variant="h6" mb={4}>
              {selectedModel} Metrics
            </MDTypography>
            <Grid container spacing={2}>
              {metrics.map((metric, i) => (
                <Grid item xs={12} sm={6} md={6} key={`model-${metric}`}>
                  <ComplexStatisticsCard
                    icon="psychology"
                    title={metric}
                    count={`${modelStats[i]}%`}
                    percentage={{ color: "success", label: "model strategy" }}
                  />
                </Grid>
              ))}
            </Grid>
          </Grid>
        </Grid>

        {/* Bar Charts */}
        <Grid container spacing={3} mt={6}>
          <Grid item xs={12} md={6}>
            <ReportsBarChart
              color="error"
              title="Random Allocation Performance"
              description="Random allocation performance across metrics"
              date="updated today"
              chart={{
                labels: metrics,
                datasets: [
                  {
                    label: "Random",
                    backgroundColor: "#ef5350",
                    data: randomStats,
                  },
                ],
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <ReportsBarChart
              color="success"
              title={`${selectedModel} Performance`}
              description="Model allocation performance across metrics"
              date="updated today"
              chart={{
                labels: metrics,
                datasets: [
                  {
                    label: selectedModel,
                    backgroundColor: "#66bb6a",
                    data: modelStats,
                  },
                ],
              }}
            />
          </Grid>
        </Grid>

        {/* Summary */}
        <MDBox mt={4}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h6" fontWeight="medium" gutterBottom>
              Summary
            </MDTypography>
            <MDTypography variant="body2" color="text">
              The model-based allocation consistently outperforms random grouping across key
              academic and wellbeing metrics. Use this view to validate improvements across model
              configurations.
            </MDTypography>
          </Card>
        </MDBox>
      </MDBox>
    </DashboardLayout>
  );
}
