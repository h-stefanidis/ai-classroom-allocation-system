// Enhanced model comparison page using real backend data and dynamic model selection with Radar Chart

import { useEffect, useState } from "react";
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
import { Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

export default function ModelComparison() {
  const [modelKeys, setModelKeys] = useState([]);
  const [model1, setModel1] = useState("");
  const [model2, setModel2] = useState("");
  const [data1, setData1] = useState(null);
  const [data2, setData2] = useState(null);

  useEffect(() => {
    const keys = Object.keys(localStorage).filter(
      (key) =>
        key.startsWith("model") &&
        !["loglevel", "isAuthenticated", "relationship_pref"].includes(key)
    );
    setModelKeys(keys);
  }, []);

  const fetchModelData = async (runNumber) => {
    if (!runNumber) {
      console.error("Missing runNumber");
      return null;
    }

    try {
      const psychoRes = await fetch(`http://127.0.0.1:5000/psychometrics-stats-normalized?run_number=${runNumber}`);
      const psychoStats = await psychoRes.json();

      if (psychoStats.error) {
        console.error("Error from psychometrics-stats-normalized:", psychoStats.error);
        return null;
      }

      return psychoStats;
    } catch (err) {
      console.error("Fetch failed:", err);
      return null;
    }
  };

  useEffect(() => {
    if (model1) {
      const runNumber = localStorage.getItem(model1);
      console.log("Fetching model1 with runNumber:", runNumber);
      fetchModelData(runNumber).then((result) => {
        if (result) setData1(result);
      });
    }
    if (model2) {
      const runNumber = localStorage.getItem(model2);
      console.log("Fetching model2 with runNumber:", runNumber);
      fetchModelData(runNumber).then((result) => {
        if (result) setData2(result);
      });
    }
  }, [model1, model2]);

  const renderRadarChart = (title, keys) => {
    if (!data1 || !data2) return null;

    const avg = (arr, key) => {
      const values = arr.map((d) => d[key]).filter((v) => typeof v === "number");
      return values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    };

    const data1Classes = data1.psychometrics_by_classroom_normalized || [];
    const data2Classes = data2.psychometrics_by_classroom_normalized || [];

    const labels = keys;
    const data1Values = keys.map((k) => avg(data1Classes, k));
    const data2Values = keys.map((k) => avg(data2Classes, k));

    return (
      <Card sx={{ p: 3, mt: 5 }}>
        <MDTypography variant="h6" gutterBottom>{title}</MDTypography>
        <Radar
          data={{
            labels,
            datasets: [
              {
                label: model1,
                data: data1Values,
                backgroundColor: "rgba(75,192,192,0.2)",
                borderColor: "rgba(75,192,192,1)",
                pointBackgroundColor: "rgba(75,192,192,1)",
              },
              {
                label: model2,
                data: data2Values,
                backgroundColor: "rgba(255,99,132,0.2)",
                borderColor: "rgba(255,99,132,1)",
                pointBackgroundColor: "rgba(255,99,132,1)",
              },
            ],
          }}
          options={{
            responsive: true,
            scales: {
              r: {
                min: 0,
                max: 1,
                ticks: { stepSize: 0.2 },
              },
            },
          }}
        />
      </Card>
    );
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Model 1</InputLabel>
              <Select value={model1} onChange={(e) => setModel1(e.target.value)}>
                {modelKeys.map((key) => (
                  <MenuItem key={key} value={key}>{key}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Model 2</InputLabel>
              <Select value={model2} onChange={(e) => setModel2(e.target.value)}>
                {modelKeys.map((key) => (
                  <MenuItem key={key} value={key}>{key}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {renderRadarChart("Psychometric Comparison", [
          "comfortable",
          "future",
          "pwi_wellbeing",
          "candidate_perc_effort",
          "growth_mindset",
          "opinion"
        ])}

        <MDBox mt={4}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h6" fontWeight="medium" gutterBottom>
              Summary
            </MDTypography>
            <MDTypography variant="body2" color="text">
              This radar chart compares average classroom-level psychometric values for the selected models.
            </MDTypography>
          </Card>
        </MDBox>
      </MDBox>
    </DashboardLayout>
  );
}
