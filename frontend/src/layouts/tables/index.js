import { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import Fade from "@mui/material/Fade";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";

import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";

const LOCAL_STORAGE_KEY = "allocationData";
const EXPIRATION_HOURS = 24;

function AllocationPage() {
  const [classroomCount, setClassroomCount] = useState(3);
  const [selectedModel, setSelectedModel] = useState("Ensemble");
  const [allocatedClassrooms, setAllocatedClassrooms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snack, setSnack] = useState({ open: false, message: "", severity: "success" });
  const [insightClassroom, setInsightClassroom] = useState(null);
  const [selectedOption, setSelectedOption] = useState("perc_academic");

  useEffect(() => {
    const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      const now = Date.now();
      const ageInHours = (now - parsed.timestamp) / (1000 * 60 * 60);
      if (ageInHours < EXPIRATION_HOURS) {
        setAllocatedClassrooms(parsed.data || []);
        setClassroomCount(parsed.count || 3);
        setSelectedModel(parsed.model || "GraphSAGE");
      } else {
        localStorage.removeItem(LOCAL_STORAGE_KEY);
      }
    }
  }, []);

  const handleFetchAllocation = async () => {
    setLoading(true);
    try {
      let data;
      console.log(selectedModel);
      if (selectedModel === "Ensemble") {
        const url = `http://127.0.0.1:5000/get_allocation_by_user_preference?classroom_count=${classroomCount}&cohort=2025`;

        // Example weights: adjust as needed or expose as inputs in UI
        const relationship_weights = {
          academic: selectedOption === "perc_academic" ? 1 : 0,
          effort: selectedOption === "perc_effort" ? 1 : 0,
          attendance: selectedOption === "perc_attendance" ? 1 : 0,
        };

        const response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ relationship_weights }),
        });

        data = await response.json();
      } else {
        const url = `http://127.0.0.1:5000/run_model2?classroomCount=${classroomCount}&option=${selectedOption}`;
        const response = await fetch(url);
        data = await response.json();
      }

      if (!data || !data.Allocations) throw new Error("No data received");

      const classroomMap = {};
      Object.entries(data.Allocations).forEach(([classroom, students]) => {
        classroomMap[classroom] = {
          id: classroom,
          students,
          disrespect: Math.floor(Math.random() * 10),
          friendships: Math.floor(Math.random() * 20),
          influence: (Math.random() * 10).toFixed(1),
          avgPerformance: {
            academic: data.AveragePerformance?.perc_academic?.[classroom] ?? null,
            effort: data.AveragePerformance?.perc_effort?.[classroom] ?? null,
            attendance: data.AveragePerformance?.perc_attendance?.[classroom] ?? null,
          },
        };
      });

      const updatedClassrooms = Object.values(classroomMap);

      localStorage.setItem(
        LOCAL_STORAGE_KEY,
        JSON.stringify({
          timestamp: Date.now(),
          model: selectedModel,
          count: classroomCount,
          data: updatedClassrooms,
        })
      );

      setAllocatedClassrooms(updatedClassrooms);
      setSnack({ open: true, message: "Allocations completed successfully!", severity: "success" });
    } catch (error) {
      console.error("Failed to fetch allocation:", error);
      setSnack({ open: true, message: "Failed to optimise allocations.", severity: "error" });
    } finally {
      setLoading(false);
    }
  };

  const handleClearAllocations = () => {
    localStorage.removeItem(LOCAL_STORAGE_KEY);
    setAllocatedClassrooms([]);
    setSnack({ open: true, message: "Allocations cleared.", severity: "info" });
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <MDBox mb={4}>
          <MDTypography variant="h4" fontWeight="bold">
            Student Allocation Panel
          </MDTypography>
          <MDTypography variant="body2" color="text" mt={1}>
            Automatically allocates students into classrooms to maximise academic performance and
            social wellbeing.
          </MDTypography>
        </MDBox>

        <Card sx={{ px: 3, py: 4, mb: 8 }}>
          <MDTypography variant="h6" mb={2}>
            Configuration
          </MDTypography>

          <Grid container spacing={2} alignItems="center" mb={2}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                select
                label="Number of Classrooms"
                value={classroomCount}
                onChange={(e) => setClassroomCount(parseInt(e.target.value))}
                size="medium"
              >
                {[1, 2, 3, 4, 5, 6].map((count) => (
                  <MenuItem key={count} value={count}>
                    {count}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl component="fieldset">
                <FormLabel component="legend">Allocation Focus</FormLabel>
                <RadioGroup
                  row
                  value={selectedOption}
                  onChange={(e) => setSelectedOption(e.target.value)}
                >
                  <FormControlLabel value="perc_academic" control={<Radio />} label="Academic" />
                  <FormControlLabel value="perc_effort" control={<Radio />} label="Effort" />
                  <FormControlLabel
                    value="perc_attendance"
                    control={<Radio />}
                    label="Attendance"
                  />
                </RadioGroup>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                select
                label="Select Model"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                size="medium"
              >
                {["Ensemble", "GraphSAGE"].map((model) => (
                  <MenuItem key={model} value={model}>
                    {model}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} md="auto">
              <Button
                variant="contained"
                color="info"
                size="large"
                onClick={handleFetchAllocation}
                disabled={loading}
              >
                {loading ? <CircularProgress color="inherit" size={24} /> : "Optimise Allocations"}
              </Button>
            </Grid>

            <Grid item xs={12} md="auto">
              <Button
                variant="contained"
                color="error"
                size="large"
                onClick={handleClearAllocations}
              >
                Clear Allocations
              </Button>
            </Grid>
          </Grid>

          <MDTypography variant="caption" color="text">
            Allocates students into {classroomCount} classrooms using the{" "}
            <strong>{selectedModel}</strong> model based on the selected metric.
          </MDTypography>
        </Card>

        {/* Classroom Cards */}
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
                    <Button
                      size="small"
                      variant="contained"
                      color="info"
                      onClick={() => setInsightClassroom(classroom)}
                    >
                      View Insights
                    </Button>
                  </MDBox>

                  <MDBox p={2} sx={{ maxHeight: 150, overflowY: "auto" }}>
                    {classroom.students.length > 0 ? (
                      classroom.students.map((student, index) => (
                        <MDBox key={student.participant_id} py={1}>
                          <MDTypography variant="body2">
                            <strong>{student.participant_id}</strong> – {student.first_name}{" "}
                            {student.last_name}
                          </MDTypography>
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

                  <MDBox px={2} py={1} bgcolor="#f9f9f9" borderTop="1px solid #e0e0e0">
                    <MDTypography variant="body2">
                      <strong>Avg. Academic:</strong>{" "}
                      {typeof classroom.avgPerformance?.academic === "number"
                        ? classroom.avgPerformance.academic.toFixed(2)
                        : "N/A"}
                    </MDTypography>
                    <MDTypography variant="body2">
                      <strong>Avg. Effort:</strong>{" "}
                      {typeof classroom.avgPerformance?.effort === "number"
                        ? classroom.avgPerformance.effort.toFixed(2)
                        : "N/A"}
                    </MDTypography>
                    <MDTypography variant="body2">
                      <strong>Avg. Attendance:</strong>{" "}
                      {typeof classroom.avgPerformance?.attendance === "number"
                        ? classroom.avgPerformance.attendance.toFixed(2)
                        : "N/A"}
                    </MDTypography>
                  </MDBox>
                </Card>
              </Grid>
            </Fade>
          ))}
        </Grid>

        {/* Insights Modal */}
        <Dialog
          open={Boolean(insightClassroom)}
          onClose={() => setInsightClassroom(null)}
          fullWidth
          maxWidth="md"
        >
          <DialogTitle>
            Classroom {insightClassroom?.id} Insights
            <IconButton
              aria-label="close"
              onClick={() => setInsightClassroom(null)}
              sx={{ position: "absolute", right: 8, top: 8 }}
            >
              <CloseIcon />
            </IconButton>
          </DialogTitle>
          <DialogContent dividers>
            {insightClassroom ? (
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <MDTypography variant="subtitle2">Disrespect Incidents:</MDTypography>
                  <MDTypography>{insightClassroom.disrespect}</MDTypography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <MDTypography variant="subtitle2">Friendships:</MDTypography>
                  <MDTypography>{insightClassroom.friendships}</MDTypography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <MDTypography variant="subtitle2">Influence Score:</MDTypography>
                  <MDTypography>{insightClassroom.influence}</MDTypography>
                </Grid>
                <Grid item xs={12}>
                  <MDTypography variant="subtitle2">Student Count:</MDTypography>
                  <MDTypography>{insightClassroom.students.length}</MDTypography>
                </Grid>
              </Grid>
            ) : (
              <MDTypography>No data available</MDTypography>
            )}
          </DialogContent>
        </Dialog>

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
      </MDBox>
    </DashboardLayout>
  );
}
export default AllocationPage;
