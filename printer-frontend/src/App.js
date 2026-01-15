import { Route, Routes } from 'react-router-dom';
import './App.css';
import Home from './components/Home.jsx';
import Queue from './components/Queue.jsx';
import NotFound from './components/NotFound.jsx';
import Success from './components/Success.jsx';
import { GuardRoute } from './components/Gaurd.jsx';

function App() {
  
  return (
    <Routes>
      <Route path='*' element={<NotFound/>}/>
      
      <Route path="/"element={<Home/>}/>
      <Route path="/print-status" element={<Queue/>} />
      <Route path='/success' element={<Success/>}/>

      </Routes>
    
  );
}

export default App;
