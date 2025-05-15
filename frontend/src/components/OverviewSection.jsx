import React from "react";
import MDBox from "components/MDBox";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";

function OverviewSection() {
  const dummyChart = {
    labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
    datasets: [
      {
        label: "Sessions",
        color: "info",
        data: [30, 50, 40, 60, 70],
      },
    ],
  };

  return (
    <MDBox py={2} px={2}>
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
