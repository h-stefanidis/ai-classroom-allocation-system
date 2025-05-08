import React, { useRef } from "react";
import LayoutWrapper from "components/LayoutWrapper";
import ForceGraph2D from "react-force-graph-2d";

const graphData = {
  nodes: [{ id: "Class 1" }, { id: "Class 2" }, { id: "Student A" }, { id: "Student B" }],
  links: [
    { source: "Student A", target: "Class 1" },
    { source: "Student B", target: "Class 2" },
  ],
};

const VisualizationPage = () => {
  const fgRef = useRef();

  return (
    <LayoutWrapper>
      <h3>Classroom Allocation Graph</h3>
      <div style={{ height: "500px" }}>
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeLabel="id"
          nodeAutoColorBy="group"
          onNodeClick={(node) => alert(`Clicked: ${node.id}`)}
        />
      </div>
    </LayoutWrapper>
  );
};

export default VisualizationPage;
