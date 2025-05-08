import React, { useState } from "react";
import { Box, Card, CardContent, Typography, TextField, Button, Grid, Rating } from "@mui/material";

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
    <Box sx={{ mt: 4 }}>
      <Grid container justifyContent="center">
        <Grid item xs={12} sm={10} md={8} lg={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Rate Your Experience
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography component="legend">Rating</Typography>
                  <Rating name="rating" value={feedback.rating} onChange={handleRatingChange} />
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
                  <Button variant="contained" color="primary" onClick={handleSubmit} sx={{ mt: 2 }}>
                    Submit Feedback
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

export default FeedbackPage;
