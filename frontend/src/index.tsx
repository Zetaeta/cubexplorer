import React from "react";
import ReactDOM from "react-dom/client";
// import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
} from "react-router-dom";
import CardsPage from "./CardsPage";
import { BASE_URL } from "./Env";
import CardPage from "./CardPage";
import { CssBaseline } from "@mui/material";
const router = createBrowserRouter(
  createRoutesFromElements([
    <Route path="/" element={<App />}></Route>,

    <Route
      path="/cards"
      element={<CardsPage />}
      loader={async () => {
        const res = await fetch(BASE_URL + "/api/cards");
        if (res.status === 404) {
          console.error(404);
          throw new Response("Not Found", { status: 404 });
        }
        return res;
      }}
    ></Route>,
    <Route
      path="/cards/:id"
      element={<CardPage />}
      loader={({ params }: { params: any }) => {
        return fetchWithError(BASE_URL + "/api/cards/" + params.id);
      }}
    ></Route>,
  ])
);
async function fetchWithError(url: string) {
  const res = await fetch(url);
  if (res.status === 404) {
    throw new Response("Not Found", { status: 404 });
  }
  return res;
}
const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);
root.render(
  <React.StrictMode>
    <CssBaseline />
    <RouterProvider router={router}></RouterProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
