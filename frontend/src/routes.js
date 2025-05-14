// React layouts
import Dashboard from "layouts/dashboard";
import Insights from "layouts/insights";
import AllocationPage from "layouts/tables";
import VisualizationPage from "pages/VisualizationPage";
import UploadDataPage from "pages/UploadDataPage";
import OnboardingPage from "pages/OnboardingPage";
import PreferencesPage from "pages/PreferencesPage";
import FeedbackPage from "pages/FeedbackPage";
import AdminToolsPage from "pages/AdminToolsPage";
import SignIn from "layouts/authentication/sign-in";
import SignUp from "layouts/authentication/sign-up";
import Profile from "layouts/profile";
import Comparison from "layouts/comparison";

// @mui icons
import Icon from "@mui/material/Icon";

const routes = [
  {
    type: "collapse",
    name: "Dashboard",
    key: "dashboard",
    icon: <Icon fontSize="small">dashboard</Icon>,
    route: "/dashboard",
    component: <Dashboard />,
  },
  {
    type: "collapse",
    name: "Insights",
    key: "insights",
    icon: <Icon fontSize="small">insights</Icon>,
    route: "/insights",
    component: <Insights />,
  },
  {
    type: "collapse",
    name: "Classroom Allocator",
    key: "classroom-allocator",
    icon: <Icon fontSize="small">hub</Icon>,
    route: "/dashboard/tables",
    component: <AllocationPage />,
  },
  {
    type: "collapse",
    name: "Visualization",
    key: "visualization",
    icon: <Icon fontSize="small">analytics</Icon>,
    route: "/dashboard/visualization",
    component: <VisualizationPage />,
  },
  {
    type: "collapse",
    name: "Model Comparison",
    key: "comparison",
    icon: <Icon fontSize="small">compare</Icon>,
    route: "/comparison",
    component: <Comparison />,
  },
  {
    type: "collapse",
    name: "Upload Data",
    key: "upload-data",
    icon: <Icon fontSize="small">upload_file</Icon>,
    route: "/upload-data",
    component: <UploadDataPage />,
  },
  {
    type: "collapse",
    name: "Onboarding",
    key: "onboarding",
    icon: <Icon fontSize="small">tour</Icon>,
    route: "/onboarding",
    component: <OnboardingPage />,
  },
  {
    type: "collapse",
    name: "Preferences",
    key: "preferences",
    icon: <Icon fontSize="small">tune</Icon>,
    route: "/preferences",
    component: <PreferencesPage />,
  },
  {
    type: "collapse",
    name: "Feedback",
    key: "feedback",
    icon: <Icon fontSize="small">feedback</Icon>,
    route: "/feedback",
    component: <FeedbackPage />,
  },
  {
    type: "collapse",
    name: "Admin Tools",
    key: "admin-tools",
    icon: <Icon fontSize="small">admin_panel_settings</Icon>,
    route: "/admin-tools",
    component: <AdminToolsPage />,
  },
  {
    type: "collapse",
    name: "Profile",
    key: "profile",
    icon: <Icon fontSize="small">person</Icon>,
    route: "/profile",
    component: <Profile />,
  },
];

export default routes;
