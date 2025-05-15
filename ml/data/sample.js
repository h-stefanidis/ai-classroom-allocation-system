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
import DataTable from "examples/Tables/DataTable";

import studentTableData from "layouts/tables/data/studentTableData";

function AllocationPage() {
  const { columns, rows } = studentTableData();
  const [classroomCount, setClassroomCount] = useState(3);
  const [allocatedClassrooms, setAllocatedClassrooms] = useState([]);

  const handleAutoAllocate = async () => {
    try {
      const response = await fetch("/get_allocation");
      const data = await response.json();

      const processedClassrooms = Object.entries(data.Allocations).map(
        ([classroomKey, studentList]) => {
          const classroomId = parseInt(classroomKey.split("_")[1]);

          const students = studentList.map((studentId) => ({
            id: studentId,
            name: `Student ${studentId}`, // Replace with actual name if provided in backend
          }));

          return {
            id: classroomId,
            students,
            totalFriendships: Math.floor(Math.random() * 10) + 5,
            retainedFriendships: Math.floor(Math.random() * 6) + 2,
            disrespectCount: Math.floor(Math.random() * 5),
          };
        }
      );

      setAllocatedClassrooms(processedClassrooms);
    } catch (error) {
      console.error("Error fetching allocation:", error);
    }
  };

  const handleDeleteClassroom = (id) => {
    setAllocatedClassrooms((prev) => prev.filter((cls) => cls.id !== id));
  };

  const handleDeleteStudent = (classroomId, studentId) => {
    setAllocatedClassrooms((prev) =>
      prev.map((cls) =>
        cls.id === classroomId
          ? { ...cls, students: cls.students.filter((s) => s.id !== studentId) }
          : cls
      )
    );
  };

  const handleReallocateStudent = (student, fromClassroomId) => {
    const toClassroom = allocatedClassrooms.find((c) => c.id !== fromClassroomId);
    if (!toClassroom) return;

    setAllocatedClassrooms((prev) =>
      prev.map((cls) => {
        if (cls.id === fromClassroomId) {
          return { ...cls, students: cls.students.filter((s) => s.id !== student.id) };
        }
        if (cls.id === toClassroom.id) {
          return { ...cls, students: [...cls.students, student] };
        }
        return cls;
      })
    );
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
                onClick={handleAutoAllocate}
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

        {/* Static Student Table */}
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <MDTypography variant="h6" color="white">
                  Student Allocation Table
                </MDTypography>
              </MDBox>
              <MDBox pt={3} px={2} pb={2}>
                <DataTable
                  table={{ columns, rows }}
                  isSorted
                  entriesPerPage
                  showTotalEntries
                  canSearch
                  noEndBorder
                />
              </MDBox>
            </Card>
          </Grid>
        </Grid>

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
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => handleDeleteClassroom(classroom.id)}
                      sx={{
                        backgroundColor: "#f44336",
                        color: "#fff",
                        "&:hover": { backgroundColor: "#d32f2f" },
                      }}
                    >
                      Delete
                    </Button>
                  </MDBox>

                  <MDBox p={2}>
                    {/* Student List */}
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
                                {student.name}
                              </MDTypography>
                              <MDBox display="flex" gap={1}>
                                <Button
                                  size="small"
                                  variant="contained"
                                  sx={{
                                    backgroundColor: "#f44336",
                                    color: "#fff",
                                    "&:hover": { backgroundColor: "#d32f2f" },
                                  }}
                                  onClick={() => handleDeleteStudenta(classroom.id, student.id)}
                                >
                                  Delete
                                </Button>

                                <Button
                                  size="small"
                                  variant="contained"
                                  sx={{
                                    backgroundColor: "#ffa726",
                                    color: "#fff",
                                    "&:hover": { backgroundColor: "#fb8c00" },
                                  }}
                                  onClick={() => handleReallocateStudent(student, classroom.id)}
                                >
                                  Reallocate
                                </Button>
                              </MDBox>
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

                    {/* Metrics */}
                    <MDTypography variant="body2" color="text" mb={1}>
                      Friendships Retained:{" "}
                      <strong>
                        {Math.round(
                          (classroom.retainedFriendships / classroom.totalFriendships) * 100
                        )}
                        % ({classroom.retainedFriendships} of {classroom.totalFriendships})
                      </strong>
                    </MDTypography>
                    <MDTypography variant="body2" color="text">
                      Disrespect Connections: <strong>{classroom.disrespectCount}</strong>
                    </MDTypography>
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
