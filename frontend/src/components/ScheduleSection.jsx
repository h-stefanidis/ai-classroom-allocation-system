import React from "react";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";

function OverviewSection() {
  const dummyChart = {
    labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
    datasets: [{ label: "Sessions", data: [30, 50, 40, 60, 70] }],
  };

  return (
    <MDBox mb={3}>
      <MDTypography variant="h6">Overview Section</MDTypography>
      <ReportsLineChart
        color="info"
        title="Class Activity"
        description="Overview of classroom usage"
        date="Updated today"
        chart={dummyChart}
      />
    </MDBox>
  );
}

export default OverviewSection;
