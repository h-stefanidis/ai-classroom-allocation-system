import { useState } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import Fade from "@mui/material/Fade";

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";

function AllocationPage() {
  const [classroomCount, setClassroomCount] = useState(3);
  const [selectedModel, setSelectedModel] = useState("GraphSAGE");
  const [allocatedClassrooms, setAllocatedClassrooms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snack, setSnack] = useState({ open: false, message: "", severity: "success" });

  const handleFetchAllocation = async () => {
    setLoading(true);
    try {
      const url =
        selectedModel === "GraphSAGE"
          ? `http://127.0.0.1:5000/run_model2?classroomCount=${classroomCount}`
          : `http://127.0.0.1:5000/get_allocation?classroom_count=${classroomCount}`;

      const response = await fetch(url);
      const data = await response.json();

      if (!data || !data.Allocations) throw new Error("No data received");

      const classroomMap = {};
      Object.entries(data.Allocations).forEach(([classroom, students]) => {
        classroomMap[classroom] = {
          id: classroom,
          students: students,
        };
      });

      setAllocatedClassrooms(Object.values(classroomMap));
      setSnack({ open: true, message: "Allocations completed successfully!", severity: "success" });
    } catch (error) {
      console.error("Failed to fetch allocation:", error);
      setSnack({ open: true, message: "Failed to optimise allocations.", severity: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        {/* Heading */}
        <MDBox mb={4}>
          <MDTypography variant="h4" fontWeight="bold">
            Student Allocation Panel
          </MDTypography>
          <MDTypography variant="body2" color="text" mt={1}>
            Automatically allocates students into classrooms to maximise academic performance and
            social wellbeing.
          </MDTypography>
        </MDBox>

        {/* Configuration Card */}
        <Card sx={{ px: 3, py: 4, mb: 8 }}>
          <MDTypography variant="h6" mb={2}>
            Configuration
          </MDTypography>

          <Grid container spacing={2} alignItems="center" mb={2}>
            {/* Classroom Count Dropdown */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                select
                label="Number of Classrooms"
                value={classroomCount}
                onChange={(e) => setClassroomCount(parseInt(e.target.value))}
                size="medium"
                InputProps={{ sx: { height: 46, fontSize: "1rem" } }}
                InputLabelProps={{ sx: { fontSize: "1rem" } }}
              >
                {[1, 2, 3, 4, 5, 6].map((count) => (
                  <MenuItem key={count} value={count}>
                    {count}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Model Dropdown */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                select
                label="Select Model"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                size="medium"
                InputProps={{ sx: { height: 46, fontSize: "1rem" } }}
                InputLabelProps={{ sx: { fontSize: "1rem" } }}
              >
                {["Ensemble", "GraphSAGE"].map((model) => (
                  <MenuItem key={model} value={model}>
                    {model}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Optimise Button */}
            <Grid item xs={12} md="auto">
              <Button
                variant="contained"
                color="info"
                size="large"
                onClick={handleFetchAllocation}
                sx={{ ml: { md: 2 }, mt: { xs: 2, md: 0 }, minWidth: 200 }}
                disabled={loading}
              >
                {loading ? <CircularProgress color="inherit" size={24} /> : "Optimise Allocations"}
              </Button>
            </Grid>
          </Grid>

          {/* Info */}
          <Grid item xs={12}>
            <MDTypography variant="caption" color="text">
              Allocates students into {classroomCount} classrooms using the{" "}
              <strong>{selectedModel}</strong> model based on academic, social, and wellbeing
              metrics.
            </MDTypography>
          </Grid>
        </Card>

        {/* Classroom Cards with Fade animation */}
        <MDBox mt={4}>
          <Grid container spacing={4}>
            {allocatedClassrooms.map((classroom) => (
              <Fade in timeout={600} key={classroom.id}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <MDBox
                      display="flex"
                      justifyContent="space-between"
                      alignItems="center"
                      px={2}
                      py={2}
                      borderBottom="1px solid #e0e0e0"
                    >
                      <MDTypography variant="h6">
                        Classroom {classroom.id} ({classroom.students.length} students)
                      </MDTypography>
                    </MDBox>
                    <MDBox p={2}>
                      <MDBox sx={{ maxHeight: 150, overflowY: "auto", mb: 2, pr: 1 }}>
                        {classroom.students.length > 0 ? (
                          classroom.students.map((student, index) => (
                            <MDBox key={student.participant_id}>
                              <MDBox
                                display="flex"
                                justifyContent="space-between"
                                alignItems="center"
                                py={1}
                              >
                                <MDTypography variant="body2" color="text">
                                  <strong>{student.participant_id}</strong> – {student.first_name}{" "}
                                  {student.last_name}
                                </MDTypography>
                              </MDBox>
                              {index < classroom.students.length - 1 && (
                                <hr style={{ border: "0.5px solid #e0e0e0" }} />
                              )}
                            </MDBox>
                          ))
                        ) : (
                          <MDTypography variant="body2" color="text">
                            No students assigned.
                          </MDTypography>
                        )}
                      </MDBox>
                    </MDBox>
                  </Card>
                </Grid>
              </Fade>
            ))}
          </Grid>
        </MDBox>
      </MDBox>

      {/* Snackbar */}
      <Snackbar
        open={snack.open}
        autoHideDuration={4000}
        onClose={() => setSnack({ ...snack, open: false })}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          severity={snack.severity}
          variant="filled"
          onClose={() => setSnack({ ...snack, open: false })}
        >
          {snack.message}
        </Alert>
      </Snackbar>
    </DashboardLayout>
  );
}

export default AllocationPage;
