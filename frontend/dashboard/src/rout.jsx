import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Dashboard from "./dashboard";
import TrendDashboard from "./trendDashboard";
import ChatBot from "./chatBot";


export function AppRouter() {

  const router = createBrowserRouter([
    { path: "/", element: <Dashboard/> },
    { path: "/trend", element: <TrendDashboard/> },
    { path: "/chatBot", element: <ChatBot /> },
    
  ]);

  return <RouterProvider router={router} />;
}