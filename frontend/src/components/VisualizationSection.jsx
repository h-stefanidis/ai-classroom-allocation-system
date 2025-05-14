import React, { useRef } from "react";
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
    <div style={{ width: "100%", height: "300px" }}>
      <ForceGraph2D
        ref={fgRef}
        graphData={data}
        nodeLabel="id"
        nodeAutoColorBy="group"
        onNodeClick={(node) => alert(`Clicked on ${node.id}`)}
      />
    </div>
  );
};

export default VisualizationSection;
