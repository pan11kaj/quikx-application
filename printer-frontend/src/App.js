import { Route, Routes } from 'react-router-dom';
import './App.css';
import Home from './components/Home.jsx';
import Queue from './components/Queue.jsx';
import NotFound from './components/NotFound.jsx';

function App() {
  return (
    <Routes>
      <Route path="/"element={<Home/>}/>
      <Route path="/print-status" element={<Queue/>} />
      <Route path='*' element={<NotFound/>}/>
      </Routes>
    
  );
}

export default App;
