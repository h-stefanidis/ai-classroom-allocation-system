export default function studentTableData() {
  return {
    columns: [
      { Header: "name", accessor: "name" },
      { Header: "grade", accessor: "grade" },
      { Header: "wellbeing", accessor: "wellbeing" },
      { Header: "status", accessor: "status" },
      { Header: "preferred friends", accessor: "friends" },
    ],
    rows: [
      {
        name: "Alice Thompson",
        grade: "6A",
        wellbeing: "High",
        status: "Unallocated",
        friends: "Ben, Clara",
      },
      {
        name: "Liam Park",
        grade: "6B",
        wellbeing: "Medium",
        status: "Allocated",
        friends: "Nina",
      },
    ],
  };
}
