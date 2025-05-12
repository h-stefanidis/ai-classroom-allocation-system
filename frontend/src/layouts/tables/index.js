import { useState } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";

function AllocationPage() {
  const [classroomCount, setClassroomCount] = useState(3);
  const [allocatedClassrooms, setAllocatedClassrooms] = useState([]);

  const handleFetchAllocation = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/get_allocation", {
        method: "GET",
      });
      const data = await response.json();

      if (!data || !data.Allocations) return;

      const classroomMap = {};

      // Group students by classroom number dynamically based on the received JSON
      Object.entries(data.Allocations).forEach(([classroom, students]) => {
        classroomMap[classroom] = {
          id: classroom,
          students: students.map((id) => ({ id })),
        }; // Ensure semicolon here
      });

      setAllocatedClassrooms(Object.values(classroomMap));
    } catch (error) {
      console.error("Failed to fetch allocation:", error);
    }
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        {/* Page Heading */}
        <MDBox mb={4}>
          <MDTypography variant="h4" fontWeight="bold">
            Student Allocation Panel
          </MDTypography>
          <MDTypography variant="body2" color="text" mt={1}>
            Automatically allocates students into classrooms to maximise academic performance and
            social wellbeing.
          </MDTypography>
        </MDBox>

        {/* Control Card */}
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

            <Grid item xs={12} md="auto">
              <Button
                variant="contained"
                color="info"
                size="large"
                onClick={handleFetchAllocation}
                sx={{ ml: { md: 2 }, mt: { xs: 2, md: 0 } }}
              >
                Optimise Allocations
              </Button>
            </Grid>
          </Grid>

          <Grid item xs={12}>
            <MDTypography variant="caption" color="text">
              Allocates students into {classroomCount} classrooms based on academic, social, and
              wellbeing metrics.
            </MDTypography>
          </Grid>
        </Card>

        {/* Dynamic Classrooms */}
        <MDBox mt={4}>
          <Grid container spacing={4}>
            {allocatedClassrooms.map((classroom) => (
              <Grid item xs={12} md={6} key={classroom.id}>
                <Card>
                  <MDBox
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    px={2}
                    py={2}
                    borderBottom="1px solid #e0e0e0"
                  >
                    <MDTypography variant="h6">{`Classroom ${classroom.id}`}</MDTypography>
                  </MDBox>

                  <MDBox p={2}>
                    <MDBox
                      sx={{
                        maxHeight: 150,
                        overflowY: "auto",
                        mb: 2,
                        pr: 1,
                      }}
                    >
                      {classroom.students.length > 0 ? (
                        classroom.students.map((student, index) => (
                          <MDBox key={student.id}>
                            <MDBox
                              display="flex"
                              justifyContent="space-between"
                              alignItems="center"
                              py={1}
                            >
                              <MDTypography variant="body2" color="text">
                                <strong>{student.id}</strong> � {student.id}
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
            ))}
          </Grid>
        </MDBox>
      </MDBox>
    </DashboardLayout>
  );
}

export default AllocationPage;
