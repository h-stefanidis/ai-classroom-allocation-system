import React, { useState } from "react";
import LayoutWrapper from "components/LayoutWrapper";
import { useDropzone } from "react-dropzone";
import {
  Card,
  CardContent,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
} from "@mui/material";

const UploadDataPage = () => {
  const [previewData, setPreviewData] = useState([]);

  const onDrop = (acceptedFiles) => {
    const reader = new FileReader();
    reader.onload = () => {
      const lines = reader.result.split("\n").map((line) => line.split(","));
      setPreviewData(lines.slice(0, 5));
    };
    reader.readAsText(acceptedFiles[0]);
  };

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  return (
    <LayoutWrapper>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Upload Data
          </Typography>
          <div
            {...getRootProps()}
            style={{ border: "2px dashed #ccc", padding: "20px", textAlign: "center" }}
          >
            <input {...getInputProps()} />
            <p>Drag & drop CSV file here, or click to select file</p>
          </div>
          {previewData.length > 0 && (
            <Table>
              <TableHead>
                <TableRow>
                  {previewData[0].map((col, idx) => (
                    <TableCell key={idx}>{col}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {previewData.slice(1).map((row, i) => (
                  <TableRow key={i}>
                    {row.map((cell, j) => (
                      <TableCell key={j}>{cell}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </LayoutWrapper>
  );
};

export default UploadDataPage;
