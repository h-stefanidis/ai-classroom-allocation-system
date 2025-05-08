import React from "react";
import { Box, Card, CardContent, Typography, Grid } from "@mui/material";

const scheduleData = [
  { time: "9:00 AM", subject: "Math", room: "101" },
  { time: "10:00 AM", subject: "Physics", room: "202" },
];

const SchedulePage = () => {
  return (
    <Box p={3} sx={{ marginLeft: "260px" }}>
      <Typography variant="h4" gutterBottom>
        Class Schedule
      </Typography>
      <Card>
        <CardContent>
          <Grid container spacing={2}>
            {scheduleData.map((entry, index) => (
              <Grid item xs={12} key={index}>
                <Typography>
                  {entry.time} - {entry.subject} (Room {entry.room})
                </Typography>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SchedulePage;
