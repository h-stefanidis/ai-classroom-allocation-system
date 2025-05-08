import React, { useRef } from "react";
import { Card, CardContent, Typography } from "@mui/material";
import ForceGraph2D from "react-force-graph-2d";

const VisualizationSection = () => {
  const fgRef = useRef();

  const data = {
    nodes: [
      { id: "Math", group: 1 },
      { id: "Physics", group: 2 },
      { id: "Chemistry", group: 3 },
      { id: "Room 101", group: 1 },
      { id: "Room 202", group: 2 },
    ],
    links: [
      { source: "Math", target: "Room 101" },
      { source: "Physics", target: "Room 202" },
      { source: "Chemistry", target: "Room 101" },
    ],
  };

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Classroom Allocation Network
        </Typography>
        <div style={{ height: "300px" }}>
          <ForceGraph2D
            ref={fgRef}
            graphData={data}
            nodeLabel="id"
            nodeAutoColorBy="group"
            onNodeClick={(node) => alert(`Clicked on ${node.id}`)}
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default VisualizationSection;
