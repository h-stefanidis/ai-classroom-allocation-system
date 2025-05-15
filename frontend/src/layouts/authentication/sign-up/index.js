import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

// @mui material components
import Card from "@mui/material/Card";
import Checkbox from "@mui/material/Checkbox";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";

// Layout
import CoverLayout from "layouts/authentication/components/CoverLayout";

// Images
import bgImage from "assets/images/sna.jpg";

function Cover() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [errorOpen, setErrorOpen] = useState(false);

  const handleSignup = async () => {
    if (!acceptedTerms) {
      setErrorOpen(true);
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: name,
          email,
          password,
          role: "student", // change as needed
        }),
      });

      if (!response.ok) throw new Error("Signup failed");

      const data = await response.json();
      console.log("✅ Signup Success:", data);

      // ✅ Corrected path
      navigate("/authentication/sign-in");
    } catch (error) {
      console.error("❌ Signup Error:", error);
      setErrorOpen(true);
      setTimeout(() => setErrorOpen(false), 3000);
    }
  };

  return (
    <>
      <CoverLayout image={bgImage}>
        <Card>
          <MDBox
            variant="gradient"
            bgColor="info"
            borderRadius="lg"
            coloredShadow="success"
            mx={2}
            mt={-3}
            p={3}
            mb={1}
            textAlign="center"
          >
            <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
              Register Your Account
            </MDTypography>
            <MDTypography display="block" variant="button" color="white" my={1}>
              Enter your email and password to sign up
            </MDTypography>
          </MDBox>
          <MDBox pt={4} pb={3} px={3}>
            <MDBox component="form" role="form" onSubmit={(e) => e.preventDefault()}>
              <MDBox mb={2}>
                <MDInput
                  type="text"
                  label="Name"
                  variant="standard"
                  fullWidth
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </MDBox>
              <MDBox mb={2}>
                <MDInput
                  type="email"
                  label="Email"
                  variant="standard"
                  fullWidth
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </MDBox>
              <MDBox mb={2}>
                <MDInput
                  type="password"
                  label="Password"
                  variant="standard"
                  fullWidth
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </MDBox>
              <MDBox display="flex" alignItems="center" ml={-1}>
                <Checkbox
                  checked={acceptedTerms}
                  onChange={() => setAcceptedTerms(!acceptedTerms)}
                />
                <MDTypography
                  variant="button"
                  fontWeight="regular"
                  color="text"
                  sx={{ cursor: "pointer", userSelect: "none", ml: -1 }}
                >
                  &nbsp;&nbsp;I agree to the&nbsp;
                </MDTypography>
                <MDTypography
                  component="a"
                  href="#"
                  variant="button"
                  fontWeight="bold"
                  color="info"
                  textGradient
                >
                  Terms and Conditions
                </MDTypography>
              </MDBox>
              <MDBox mt={4} mb={1}>
                <MDButton variant="gradient" color="info" fullWidth onClick={handleSignup}>
                  sign up
                </MDButton>
              </MDBox>
              <MDBox mt={3} mb={1} textAlign="center">
                <MDTypography variant="button" color="text">
                  Already have an account?{" "}
                  <MDTypography
                    component={Link}
                    to="/authentication/sign-in"
                    variant="button"
                    color="info"
                    fontWeight="medium"
                    textGradient
                  >
                    Sign In
                  </MDTypography>
                </MDTypography>
              </MDBox>
            </MDBox>
          </MDBox>
        </Card>
      </CoverLayout>

      {/* Snackbar for signup errors */}
      <Snackbar
        open={errorOpen}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        autoHideDuration={3000}
      >
        <Alert severity="error" variant="filled" sx={{ width: "100%" }}>
          Failed to register. Please try again.
        </Alert>
      </Snackbar>
    </>
  );
}

export default Cover;
