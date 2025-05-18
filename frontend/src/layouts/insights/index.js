// src/layouts/insights/index.js

import { useEffect, useState } from "react";
import axios from "axios";

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

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LabelList,
} from "recharts";

function Insights() {
  const [psychometricsData, setPsychometricsData] = useState(null);
  const [relationshipData, setRelationshipData] = useState(null);
  const [selectedAttributes, setSelectedAttributes] = useState([]);
  const [compareAttrX, setCompareAttrX] = useState("comfortable");
  const [compareAttrY, setCompareAttrY] = useState("growth_mindset");

  useEffect(() => {
    axios
      .get(
        "http://127.0.0.1:5000/psychometrics-stats-normalized?run_number=f9e1220c-cf75-483a-832a-fe457be21732"
      )
      .then((response) => {
        const { psychometrics_by_classroom_normalized, relationship_preservation } = response.data;
        setPsychometricsData(psychometrics_by_classroom_normalized);
        setRelationshipData(relationship_preservation);

        const example = psychometrics_by_classroom_normalized?.[0];
        if (example) {
          const attrs = Object.keys(example).filter((key) => key !== "classroom_id");
          setSelectedAttributes(attrs);
        }
      })
      .catch((error) => {
        console.error("Failed to fetch insights data:", error);
      });
  }, []);

  const getRadarChartData = () => {
    if (!psychometricsData) return [];
    return selectedAttributes.map((key) => {
      const entry = { attribute: key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()) };
      psychometricsData.forEach((c) => {
        entry[`Class ${c.classroom_id}`] = c[key] ?? 0;
      });
      return entry;
    });
  };

  const getComparisonData = () => {
    if (!psychometricsData) return [];
    return psychometricsData.map((c) => ({
      name: `Class ${c.classroom_id}`,
      [compareAttrX]: Number(c[compareAttrX]?.toFixed(2) || 0),
      [compareAttrY]: Number(c[compareAttrY]?.toFixed(2) || 0),
    }));
  };

  const getRelationshipChartData = (type) => {
    if (!relationshipData || !relationshipData[type]) return [];
    return relationshipData[type].map((entry) => ({
      name: `Class ${entry.classroom_id}`,
      preserved: entry.percentage,
    }));
  };

  const relationshipTypes = ["friend", "advice", "feedback", "influence", "more_time"];

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
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
              count={psychometricsData?.length || 0}
              percentage={{ color: "info", label: "configured in this run" }}
            />
          </Grid>
        </Grid>

        {/* Comparison Bar Chart */}
        {psychometricsData && (
          <MDBox mt={10}>
            <Card>
              <MDBox p={2}>
                <MDTypography variant="h6" fontWeight="medium">
                  Compare Key Psychometric Attributes
                </MDTypography>
                <Grid container spacing={2} mt={1}>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Attribute X</InputLabel>
                      <Select
                        value={compareAttrX}
                        onChange={(e) => setCompareAttrX(e.target.value)}
                      >
                        {selectedAttributes.map((attr) => (
                          <MenuItem key={attr} value={attr}>
                            {attr.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Attribute Y</InputLabel>
                      <Select
                        value={compareAttrY}
                        onChange={(e) => setCompareAttrY(e.target.value)}
                      >
                        {selectedAttributes.map((attr) => (
                          <MenuItem key={attr} value={attr}>
                            {attr.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </MDBox>
              <MDBox height="350px" px={2}>
                <ResponsiveContainer>
                  <BarChart
                    data={getComparisonData()}
                    margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey={compareAttrX} fill="#3A416F">
                      <LabelList dataKey={compareAttrX} position="top" />
                    </Bar>
                    <Bar dataKey={compareAttrY} fill="#82ca9d">
                      <LabelList dataKey={compareAttrY} position="top" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </MDBox>
            </Card>
          </MDBox>
        )}

        {/* Relationship Preservation Section */}
        {relationshipData && (
          <MDBox mt={10}>
            <Grid container spacing={3}>
              {relationshipTypes.map((type) => (
                <Grid item xs={12} md={6} key={type}>
                  <Card>
                    <MDBox p={2}>
                      <MDTypography variant="h6" fontWeight="medium">
                        {type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}{" "}
                        Relationships Preserved
                      </MDTypography>
                    </MDBox>
                    <MDBox height="300px" px={2}>
                      <ResponsiveContainer>
                        <BarChart data={getRelationshipChartData(type)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                          <Tooltip formatter={(v) => `${v}%`} />
                          <Bar dataKey="preserved" fill="#66bb6a">
                            <LabelList
                              dataKey="preserved"
                              position="top"
                              formatter={(v) => `${v}%`}
                            />
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </MDBox>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </MDBox>
        )}

        {/* Radar Chart Section */}
        {psychometricsData && (
          <MDBox mt={10}>
            <Card>
              <MDBox p={2}>
                <MDTypography variant="h6" fontWeight="medium">
                  Psychometric Comparison (Radar)
                </MDTypography>
                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel>Select Attributes</InputLabel>
                  <Select
                    multiple
                    value={selectedAttributes}
                    onChange={(e) => setSelectedAttributes(e.target.value)}
                    label="Select Attributes"
                    renderValue={(selected) => selected.join(", ")}
                  >
                    {psychometricsData &&
                      Object.keys(psychometricsData[0])
                        .filter((key) => key !== "classroom_id")
                        .map((attr) => (
                          <MenuItem key={attr} value={attr}>
                            {attr.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                          </MenuItem>
                        ))}
                  </Select>
                </FormControl>
              </MDBox>
              <MDBox height="400px" pb={2} px={2}>
                <ResponsiveContainer>
                  <RadarChart outerRadius={130} data={getRadarChartData()}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="attribute" />
                    <PolarRadiusAxis angle={30} domain={[0, 1]} />
                    {psychometricsData.map((c, index) => (
                      <Radar
                        key={index}
                        name={`Class ${c.classroom_id}`}
                        dataKey={`Class ${c.classroom_id}`}
                        stroke={index % 2 === 0 ? "#3A416F" : "#82ca9d"}
                        fill={index % 2 === 0 ? "#3A416F" : "#82ca9d"}
                        fillOpacity={0.4}
                      />
                    ))}
                    <Tooltip />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </MDBox>
            </Card>
          </MDBox>
        )}
      </MDBox>
    </DashboardLayout>
  );
}

export default Insights;
