import 'bootstrap/dist/css/bootstrap.min.css';
import MenuEditor from './MenuEditor';
import MenuWizard from './menuWizard';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/menu-editor/create" element={<MenuWizard />} />
        <Route path="/menu-editor/:menuId/*" element={<MenuEditor />} />
        <Route path="/" element={<NavigateToMenuList />} />
        {/* Optionally, add a default route */}
        {/* <Route path="*" element={<MenuEditor />} /> */}
      </Routes>
    </BrowserRouter>
  );
}

function NavigateToMenuList() {
  useEffect(() => {
    window.location.href = '/menus/';
  }, []);
  return null;
}

export default App;