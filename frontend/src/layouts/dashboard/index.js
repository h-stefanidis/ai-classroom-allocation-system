import React, { useEffect, useState } from "react";
import axios from "axios";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
  LabelList
} from "recharts";

export default function Dashboard() {
  const [chartData, setChartData] = useState([]);
  const [summary, setSummary] = useState({});
  const [snaByClass, setSnaByClass] = useState([]);
  const [betweennessBars, setBetweennessBars] = useState([]);
  const [relationshipDensity, setRelationshipDensity] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:5000/allocation-runs").then((res) => {
      const runs = res.data.runs || [];
      const formatted = runs.map((run, index) => ({
        name: `Run ${index + 1}`,
        students: 45 - index * 5, // Placeholder
      }));
      setChartData(formatted);
    });

    axios.get("http://localhost:5000/group-relationship-summary").then((res) => {
      setSummary(res.data);
    });

    axios.get("http://localhost:5000/sna_by_run_number").then((res) => {
      const data = res.data;

      const lineData = data.map(item => ({
        classroom_id: `Class ${item.classroom_id}`,
        num_edges: item.num_edges,
        num_nodes: item.num_nodes
      }));
      setSnaByClass(lineData);

      const bars = [];
      data.forEach(item => {
        item.top_betweenness.forEach(node => {
          bars.push({
            classroom: `Class ${item.classroom_id}`,
            name: node.name,
            value: node.value
          });
        });
      });
      setBetweennessBars(bars);
    });

    axios.get("http://localhost:5000/sna_by_run_number_in_types_of_relationship").then((res) => {
      const json = res.data;
      const result = [];

      Object.keys(json).forEach((type) => {
        const entries = json[type];
        if (entries.length > 0) {
          const totalEdges = entries.reduce((sum, entry) => sum + entry.num_edges, 0);
          const totalNodes = entries.reduce((sum, entry) => sum + entry.num_nodes, 0);
          const count = entries.length;
          result.push({
            relationship_type: type,
            avg_edges: +(totalEdges / count).toFixed(2),
            avg_nodes: +(totalNodes / count).toFixed(2)
          });
        }
      });

      setRelationshipDensity(result);
    });
  }, []);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={3}>
            <ComplexStatisticsCard
              icon="people"
              title="Friendship Retained"
              count={summary.avg_friendship_retained || "-"}
              percentage={{ color: "success", label: "cohort avg" }}
            />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <ComplexStatisticsCard
              icon="psychology"
              title="Engagement"
              count={summary.avg_engagement_score || "-"}
              percentage={{ color: "info", label: "survey derived" }}
            />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <ComplexStatisticsCard
              icon="verified"
              title="Stability"
              count={summary.avg_stability || "-"}
              percentage={{ color: "warning", label: "network metric" }}
            />
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <ComplexStatisticsCard
              icon="insights"
              title="Behavior Rating"
              count={summary.avg_behavior_rating || "-"}
              percentage={{ color: "secondary", label: "scale 1–5" }}
            />
          </Grid>
        </Grid>

        {/* <MDBox mt={4}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h5" fontWeight="medium" gutterBottom>
              Allocation Runs
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
        </MDBox> */}

        <MDBox mt={4}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h5" fontWeight="medium" gutterBottom>
              Network Density per Classroom
            </MDTypography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={snaByClass}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="classroom_id" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="num_edges" stroke="#8884d8" name="Edges" />
                <Line type="monotone" dataKey="num_nodes" stroke="#82ca9d" name="Nodes" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </MDBox>

        <MDBox mt={4}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h5" fontWeight="medium" gutterBottom>
              Top 5 Betweenness Centrality (per Classroom)
            </MDTypography>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                layout="vertical"
                data={betweennessBars}
                margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#1976d2" name="Betweenness">
                  <LabelList dataKey="classroom" position="right" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </MDBox>

        <MDBox mt={4}>
          <Card sx={{ p: 3 }}>
            <MDTypography variant="h5" fontWeight="medium" gutterBottom>
              Network Density by Relationship Type
            </MDTypography>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={relationshipDensity}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="relationship_type" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="avg_edges" fill="#82ca9d" name="Avg Edges" />
                <Bar dataKey="avg_nodes" fill="#8884d8" name="Avg Nodes" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </MDBox>
      </MDBox>
    </DashboardLayout>
  );
}
