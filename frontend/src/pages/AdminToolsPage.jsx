import React, { useState } from "react";
import { Grid, Card, CardContent, TextField, Button } from "@mui/material";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

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
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          {/* Room Management Card */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <MDTypography variant="h6" fontWeight="medium" gutterBottom>
                  Room Management
                </MDTypography>
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
                <Button variant="contained" color="info" onClick={handleRoomSubmit} sx={{ mt: 2 }}>
                  Save Room
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* User Management Card */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <MDTypography variant="h6" fontWeight="medium" gutterBottom>
                  User Management
                </MDTypography>
                <TextField
                  fullWidth
                  label="User Email"
                  margin="normal"
                  value={user.email}
                  onChange={(e) => setUser({ ...user, email: e.target.value })}
                />
                <TextField
                  fullWidth
                  label="Role (e.g., student / teacher)"
                  margin="normal"
                  value={user.role}
                  onChange={(e) => setUser({ ...user, role: e.target.value })}
                />
                <Button variant="contained" color="info" onClick={handleUserSubmit} sx={{ mt: 2 }}>
                  Save User
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
    </DashboardLayout>
  );
};

export default AdminToolsPage;
