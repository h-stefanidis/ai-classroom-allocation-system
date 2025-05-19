import React, { useState } from "react";
import {
  Box,
  Button,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  Container,
} from "@mui/material";

const UploadDataPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [summary, setSummary] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setMessage("");
    setError("");
    setSummary(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a file.");
      return;
    }

    setUploading(true);
    setMessage("");
    setError("");
    setSummary(null);

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("cohort", 2000); // ✅ Send cohort value

    try {
      const response = await fetch("http://localhost:5000/upload-excel", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      console.log("Upload result:", result);

      if (response.ok) {
        setMessage(result.message);
        setSummary({
          rows: result.rows,
          columns: result.columns || [],
          cohort: result.cohort,
        });
      } else {
        setError(result.error || "Upload failed.");
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Something went wrong during upload.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 8 }}>
        <Paper
          elevation={3}
          sx={{
            p: 4,
            borderRadius: 2,
            bgcolor: "#ffffff",
            maxWidth: 800,
            mx: "auto",
          }}
        >
          <Typography variant="h4" fontWeight={600} mb={3}>
            Upload Excel File
          </Typography>

          <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
            <Button
              variant="outlined"
              component="label"
              sx={{ width: "fit-content", textTransform: "none" }}
            >
              📁 Choose File
              <input hidden type="file" onChange={handleFileChange} accept=".xlsx, .xls" />
            </Button>

            <Typography variant="body2" sx={{ mt: -1, color: "gray" }}>
              {selectedFile ? selectedFile.name : "No file selected"}
            </Typography>

            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              disabled={uploading}
              sx={{
                mt: 2,
                px: 4,
                py: 1,
                textTransform: "none",
                transition: "all 0.2s ease-in-out",
                "&:hover": { backgroundColor: "#1565c0" },
              }}
            >
              {uploading ? <CircularProgress size={22} color="inherit" /> : "Upload"}
            </Button>

            {message && (
              <Alert
                severity="success"
                sx={{
                  mt: 3,
                  width: "100%",
                  animation: "fadeIn 0.5s ease",
                  "@keyframes fadeIn": {
                    from: { opacity: 0 },
                    to: { opacity: 1 },
                  },
                }}
              >
                ✅ {message}
              </Alert>
            )}

            {error && (
              <Alert severity="error" sx={{ mt: 3, width: "100%" }}>
                {error}
              </Alert>
            )}
          </Box>

          {summary?.columns?.length > 0 && (
            <Paper variant="outlined" sx={{ mt: 4, p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Upload Summary
              </Typography>
              <List>
                <ListItem>
                  <ListItemText primary={`Rows: ${summary.rows}`} />
                </ListItem>
                <ListItem>
                  <ListItemText primary={`Cohort: ${summary.cohort}`} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Columns:" />
                </ListItem>
                {summary.columns.map((col, idx) => (
                  <ListItem key={idx} sx={{ pl: 4 }}>
                    <ListItemText primary={col} />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default UploadDataPage;
