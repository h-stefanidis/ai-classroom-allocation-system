import React, { useState } from "react";
import { Card, CardContent, Typography, TextField, Button, Grid, Box } from "@mui/material";

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
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Grid container justifyContent="center">
        <Grid item xs={12} sm={10} md={8} lg={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Submit Your Preferences
              </Typography>

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
                  <Button variant="contained" color="primary" onClick={handleSubmit} sx={{ mt: 2 }}>
                    Submit Preferences
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default PreferencesPage;
