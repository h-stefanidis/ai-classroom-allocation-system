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
  const [selectedModel, setSelectedModel] = useState("GraphSAGE");
  const [allocatedClassrooms, setAllocatedClassrooms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snack, setSnack] = useState({ open: false, message: "", severity: "success" });
  const [insightClassroom, setInsightClassroom] = useState(null);
  const [selectedOption, setSelectedOption] = useState("perc_academic");
  const [lastRunNumber, setLastRunNumber] = useState(null);

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

        const model = parsed.model || "GraphSAGE";
        setSelectedModel(model);
        const run = localStorage.getItem(`${model}_lastRunNumber`);
        if (run) setLastRunNumber(run);
      } else {
        localStorage.removeItem(LOCAL_STORAGE_KEY);
      }
    }
  }, []);

  const fetchAndInjectPsychometrics = async (runNumber, classroomMap) => {
    const statsRes = await fetch(
      `http://127.0.0.1:5000/psychometrics-stats-normalized?run_number=${runNumber}`
    );
    const statsData = await statsRes.json();

    statsData.psychometrics_by_classroom_normalized.forEach((entry) => {
      const id = entry.classroom_id;
      if (classroomMap[id]) {
        classroomMap[id].psychometrics = {
          growth_mindset: entry.growth_mindset,
          comfortable: entry.comfortable,
          isolated: entry.isolated,
          criticises: entry.criticises,
          manbox5_overall: entry.manbox5_overall,
          wellbeing: entry.pwi_wellbeing,
        };
      }
    });

    statsData.relationship_preservation.friend.forEach((entry) => {
      const id = entry.classroom_id;
      if (classroomMap[id]) {
        classroomMap[id].relationships = {
          friendsPreserved: entry.percentage,
        };
      }
    });

    statsData.relationship_preservation.advice.forEach((entry) => {
      const id = entry.classroom_id;
      if (classroomMap[id]) {
        classroomMap[id].relationships.advicePreserved = entry.percentage;
      }
    });

    statsData.relationship_preservation.influence.forEach((entry) => {
      const id = entry.classroom_id;
      if (classroomMap[id]) {
        classroomMap[id].relationships.influencePreserved = entry.percentage;
      }
    });
  };

  const handleFetchAllocation = async () => {
    setLoading(true);
    try {
      let url = "";
      if (selectedModel === "Latest") {
        url = `http://127.0.0.1:5000/get_allocation`;
      } else if (selectedModel === "ByPreference") {
        url = `http://127.0.0.1:5000/get_allocation_by_user_preference?option=${selectedOption}`;
      } else {
        url = `http://127.0.0.1:5000/run_model2?classroomCount=${classroomCount}&option=${selectedOption}`;
      }

      const response = await fetch(url);
      const data = await response.json();
      if (!data || !data.Allocations) throw new Error("No data received");

      // Prepare classroomMap
      const classroomMap = {};
      Object.entries(data.Allocations).forEach(([classroom, students]) => {
        classroomMap[classroom] = {
          id: classroom,
          students,
          avgPerformance: {
            academic: data.AveragePerformance?.perc_academic?.[classroom] ?? null,
            effort: data.AveragePerformance?.perc_effort?.[classroom] ?? null,
            attendance: data.AveragePerformance?.perc_attendance?.[classroom] ?? null,
          },
        };
      });

      const updatedClassrooms = Object.values(classroomMap);

      // Store in local storage (if needed)
      if (selectedModel === "GraphSAGE" || selectedModel === "Ensemble") {
        localStorage.setItem(
          LOCAL_STORAGE_KEY,
          JSON.stringify({
            timestamp: Date.now(),
            model: selectedModel,
            count: classroomCount,
            data: updatedClassrooms,
          })
        );

        if (data.run_number !== undefined) {
          localStorage.setItem(`${selectedModel}_lastRunNumber`, data.run_number);
          setLastRunNumber(data.run_number);

          if (data.run_number !== undefined) {
            localStorage.setItem(`${selectedModel}_lastRunNumber`, data.run_number);
            setLastRunNumber(data.run_number);

            // ✅ Call the helper
            await fetchAndInjectPsychometrics(data.run_number, classroomMap);
          }

          // Inject key stats into classroomMap
          statsData.psychometrics_by_classroom_normalized.forEach((entry) => {
            const id = entry.classroom_id;
            if (classroomMap[id]) {
              classroomMap[id].psychometrics = {
                growth_mindset: entry.growth_mindset,
                comfortable: entry.comfortable,
                isolated: entry.isolated,
                criticises: entry.criticises,
                manbox5_overall: entry.manbox5_overall,
                wellbeing: entry.pwi_wellbeing,
              };
            }
          });

          statsData.relationship_preservation.friend.forEach((entry) => {
            const id = entry.classroom_id;
            if (classroomMap[id]) {
              classroomMap[id].relationships = {
                friendsPreserved: entry.percentage,
              };
            }
          });

          statsData.relationship_preservation.advice.forEach((entry) => {
            const id = entry.classroom_id;
            if (classroomMap[id]) {
              classroomMap[id].relationships.advicePreserved = entry.percentage;
            }
          });

          statsData.relationship_preservation.influence.forEach((entry) => {
            const id = entry.classroom_id;
            if (classroomMap[id]) {
              classroomMap[id].relationships.influencePreserved = entry.percentage;
            }
          });
        }
      }

      setAllocatedClassrooms(Object.values(classroomMap));
      setSnack({
        open: true,
        message: `Allocations loaded successfully! ${
          data.run_number !== undefined ? `(Run #${data.run_number})` : ""
        }`,
        severity: "success",
      });
    } catch (error) {
      console.error("Failed to fetch allocation:", error);
      setSnack({ open: true, message: "Failed to load allocation.", severity: "error" });
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
                onChange={(e) => {
                  const model = e.target.value;
                  setSelectedModel(model);
                  const storedRun = localStorage.getItem(`${model}_lastRunNumber`);
                  if (storedRun) {
                    setLastRunNumber(storedRun);
                  } else {
                    setLastRunNumber(null);
                  }
                }}
                size="medium"
              >
                {["GraphSAGE", "Ensemble", "Latest", "ByPreference"].map((model) => (
                  <MenuItem key={model} value={model}>
                    {model}
                  </MenuItem>
                ))}
              </TextField>

              {lastRunNumber && (
                <MDTypography variant="caption" color="text">
                  Last run for <strong>{selectedModel}</strong>: #{lastRunNumber}
                </MDTypography>
              )}
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
                  {classroom.psychometrics && (
                    <MDBox px={2} py={1} mt={1} bgcolor="#f0f0f0">
                      <MDTypography variant="body2">
                        <strong>Growth Mindset:</strong>{" "}
                        {classroom.psychometrics.growth_mindset.toFixed(2)}
                      </MDTypography>
                      <MDTypography variant="body2">
                        <strong>Comfortable:</strong>{" "}
                        {classroom.psychometrics.comfortable.toFixed(2)}
                      </MDTypography>
                      <MDTypography variant="body2">
                        <strong>Isolated:</strong> {classroom.psychometrics.isolated.toFixed(2)}
                      </MDTypography>
                      <MDTypography variant="body2">
                        <strong>Criticises:</strong> {classroom.psychometrics.criticises.toFixed(2)}
                      </MDTypography>
                      <MDTypography variant="body2">
                        <strong>Manbox Attitudes:</strong>{" "}
                        {classroom.psychometrics.manbox5_overall.toFixed(2)}
                      </MDTypography>
                      <MDTypography variant="body2">
                        <strong>Wellbeing:</strong> {classroom.psychometrics.wellbeing.toFixed(2)}
                      </MDTypography>
                    </MDBox>
                  )}

                  {classroom.relationships && (
                    <MDBox px={2} py={1} bgcolor="#fafafa">
                      <MDTypography variant="body2">
                        <strong>Friendships Preserved:</strong>{" "}
                        {classroom.relationships.friendsPreserved.toFixed(1)}%
                      </MDTypography>
                      <MDTypography variant="body2">
                        <strong>Advice Links Preserved:</strong>{" "}
                        {classroom.relationships.advicePreserved.toFixed(1)}%
                      </MDTypography>
                      <MDTypography variant="body2">
                        <strong>Influence Links Preserved:</strong>{" "}
                        {classroom.relationships.influencePreserved.toFixed(1)}%
                      </MDTypography>
                    </MDBox>
                  )}
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
