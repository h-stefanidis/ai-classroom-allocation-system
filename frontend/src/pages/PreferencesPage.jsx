import React, { useState } from "react";
import { Grid, Card, CardContent, TextField, Button } from "@mui/material";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

function PreferencesPage() {
  const [formData, setFormData] = useState({
    preferredTime: "",
    preferredRoom: "",
    comments: "",
  });

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = () => {
    console.log("Submitted Preferences:", formData);
    // Placeholder for future API integration
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container justifyContent="center">
          <Grid item xs={12} sm={10} md={8} lg={6}>
            <Card elevation={3}>
              <CardContent>
                <MDTypography variant="h5" fontWeight="medium" gutterBottom>
                  Submit Your Preferences
                </MDTypography>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Preferred Time"
                      name="preferredTime"
                      value={formData.preferredTime}
                      onChange={handleChange}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Preferred Room"
                      name="preferredRoom"
                      value={formData.preferredRoom}
                      onChange={handleChange}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Additional Comments"
                      name="comments"
                      value={formData.comments}
                      onChange={handleChange}
                      multiline
                      rows={3}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button variant="contained" color="info" onClick={handleSubmit} sx={{ mt: 2 }}>
                      Submit Preferences
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
    </DashboardLayout>
  );
}

export default PreferencesPage;
