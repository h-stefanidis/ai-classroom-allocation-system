import React from "react";
import PropTypes from "prop-types";
import MDBox from "components/MDBox";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";

const LayoutWrapper = ({ children }) => {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>{children}</MDBox>
    </DashboardLayout>
  );
};

LayoutWrapper.propTypes = {
  children: PropTypes.node.isRequired,
};

export default LayoutWrapper;
