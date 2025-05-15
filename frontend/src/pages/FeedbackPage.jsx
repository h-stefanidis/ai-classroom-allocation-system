import React, { useState } from "react";
import { Grid, Card, CardContent, TextField, Button, Rating } from "@mui/material";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

function FeedbackPage() {
  const [feedback, setFeedback] = useState({
    rating: 0,
    comment: "",
  });

  const handleChange = (e) => {
    setFeedback((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleRatingChange = (event, newValue) => {
    setFeedback((prev) => ({
      ...prev,
      rating: newValue,
    }));
  };

  const handleSubmit = () => {
    console.log("Submitted Feedback:", feedback);
    alert("Feedback submitted (mock)");
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
                  Rate Your Experience
                </MDTypography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <MDTypography variant="button" fontWeight="regular" color="text">
                      Rating
                    </MDTypography>
                    <Rating
                      name="rating"
                      value={feedback.rating}
                      onChange={handleRatingChange}
                      size="large"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Comments"
                      name="comment"
                      value={feedback.comment}
                      onChange={handleChange}
                      multiline
                      rows={4}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button variant="contained" color="info" onClick={handleSubmit} sx={{ mt: 2 }}>
                      Submit Feedback
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

export default FeedbackPage;
