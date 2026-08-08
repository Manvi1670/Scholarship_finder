import {useState} from 'react'
import { BrowserRouter,Route,Routes } from 'react-router-dom'
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import ScholarshipDetailPage from './components/ScholarshipdetailPage'
import ProfilePage from './components/ProfilePage';
import Navbar from './components/Navbar/Navbar';
import HomePage from './components/HomePage';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';
import backgroundImage from './assets/Images/bg.png';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
      <Navbar />
      <ErrorBoundary>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/scholarship/:id" element={<ScholarshipDetailPage />} />
        </Routes>
      </ErrorBoundary>
    </BrowserRouter>
    </div>

  )
}

export default App