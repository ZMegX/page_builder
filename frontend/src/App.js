import 'bootstrap/dist/css/bootstrap.min.css';
import MenuEditor from './MenuEditor';
import MenuCreate from './MenuCreate';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/menu-editor/create" element={<MenuCreate />} />
        <Route path="/menu-editor/*" element={<MenuEditor />} />
        {/* Optionally, add a default route */}
        <Route path="*" element={<MenuEditor />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;