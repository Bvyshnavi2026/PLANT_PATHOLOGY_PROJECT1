import { useState } from 'react'
import './App.css'
import Header from './components/Header'
import Footer from  './components/Footer'
import 'bootstrap/dist/css/bootstrap.min.css'
function App() {
  
return (
  <>
    <Header />

    <div className="container mt-5 text-center">

      <h1 className="text-success">
        🌿 Plant Pathology Disease Detection
      </h1>

      <p>
        Upload a plant leaf image to identify the disease.
      </p>

      <div className="card p-4 shadow mt-4">

        <h3>Upload Plant Leaf Image</h3>

        <input
          type="file"
          className="form-control mt-3"
          accept="image/*"
        />

        <button className="btn btn-success mt-3">
          Predict Disease
        </button>

        <hr />

        <h4>Prediction Result</h4>
        <p>No prediction yet.</p>

        <h4>Treatment</h4>
        <p>Treatment details will appear here.</p>

      </div>

    </div>

    <Footer />
  </>
);   
}
export default App
