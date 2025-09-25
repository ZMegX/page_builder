import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

document.addEventListener("DOMContentLoaded", function () {
const root = document.getElementById("react-root") || document.getElementById("root");
  if (root) {
    ReactDOM.createRoot(root).render(<App />);
  }
}); 