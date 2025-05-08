import React from "react";
import LayoutWrapper from "components/LayoutWrapper";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import MDTypography from "components/MDTypography";

const data = [
  { name: "Week 1", students: 40 },
  { name: "Week 2", students: 45 },
  { name: "Week 3", students: 50 },
];

const OverviewPage = () => {
  return (
    <LayoutWrapper>
      <MDTypography variant="h4" gutterBottom>
        Overview
      </MDTypography>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="students" stroke="#8884d8" activeDot={{ r: 8 }} />
        </LineChart>
      </ResponsiveContainer>
    </LayoutWrapper>
  );
};

export default OverviewPage;
