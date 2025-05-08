import React, { useState } from "react";
import { Box, Card, CardContent, Typography, TextField, Button, Grid } from "@mui/material";

const AdminToolsPage = () => {
  const [room, setRoom] = useState({ name: "", capacity: "", equipment: "" });
  const [user, setUser] = useState({ email: "", role: "" });

  const handleRoomSubmit = () => {
    console.log("Room Data Submitted:", room);
  };

  const handleUserSubmit = () => {
    console.log("User Data Submitted:", user);
  };

  return (
    <Box p={3} sx={{ marginLeft: "260px" }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Room Management
              </Typography>
              <TextField
                fullWidth
                label="Room Name"
                margin="normal"
                value={room.name}
                onChange={(e) => setRoom({ ...room, name: e.target.value })}
              />
              <TextField
                fullWidth
                label="Capacity"
                margin="normal"
                value={room.capacity}
                onChange={(e) => setRoom({ ...room, capacity: e.target.value })}
              />
              <TextField
                fullWidth
                label="Equipment"
                margin="normal"
                value={room.equipment}
                onChange={(e) => setRoom({ ...room, equipment: e.target.value })}
              />
              <Button variant="contained" color="primary" onClick={handleRoomSubmit}>
                Save Room
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                User Management
              </Typography>
              <TextField
                fullWidth
                label="User Email"
                margin="normal"
                value={user.email}
                onChange={(e) => setUser({ ...user, email: e.target.value })}
              />
              <TextField
                fullWidth
                label="Role (e.g., student/teacher)"
                margin="normal"
                value={user.role}
                onChange={(e) => setUser({ ...user, role: e.target.value })}
              />
              <Button variant="contained" color="secondary" onClick={handleUserSubmit}>
                Save User
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdminToolsPage;
