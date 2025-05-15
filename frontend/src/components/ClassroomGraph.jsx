import React, { useEffect, useRef } from "react";
import PropTypes from "prop-types";
import cytoscape from "cytoscape";

const ClassroomGraph = ({ elements, subgraphEdges, selectedAction, classroom }) => {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      layout: { name: "cose" },
    });

    cyRef.current = cy;

    const baseStyle = [
      {
        selector: "node",
        style: {
          label: "data(label)",
          "background-color": "#0074D9",
          "text-valign": "center",
          color: "#fff",
          "font-size": 10,
          "text-outline-width": 2,
          "text-outline-color": "#000",
        },
      },
      {
        selector: "edge",
        style: {
          width: 3,
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
        },
      },
      {
        selector: `edge[classroom = "${classroom}"]`,
        style: {
          "line-color": "#0074D9",
          "target-arrow-color": "#0074D9",
        },
      },
      {
        selector: `edge[classroom != "${classroom}"]`,
        style: {
          "line-color": "#FF851B",
          "target-arrow-color": "#FF851B",
        },
      },
    ];

    const subgraphStyle = subgraphEdges.map((edgeKey) => ({
      selector: `edge[id = "${edgeKey}"]`,
      style: {
        "line-color": "#FF4136",
        "target-arrow-color": "#FF4136",
      },
    }));

    const selectedActionStyle = selectedAction
      ? [
          {
            selector: `edge[source = "${selectedAction}"]`,
            style: {
              "line-color": "#B10DC9",
              "target-arrow-color": "#B10DC9",
            },
          },
        ]
      : [];

    cy.style([...baseStyle, ...subgraphStyle, ...selectedActionStyle]);
  }, [elements, subgraphEdges, selectedAction, classroom]);

  return <div ref={containerRef} style={{ width: "100%", height: "400px" }} />;
};

ClassroomGraph.propTypes = {
  elements: PropTypes.array.isRequired,
  subgraphEdges: PropTypes.array.isRequired,
  selectedAction: PropTypes.string,
  classroom: PropTypes.string.isRequired,
};

export default ClassroomGraph;
