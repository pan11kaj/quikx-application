
import React, { useState } from 'react';
import '../styles/feedback.css';
import axios from 'axios';
import toast, { Toaster } from "react-hot-toast";

export default function ReportPage() {
  const [data, setData] = useState({
    phone: '',
    file_id: '',
    problem: ''
  });
  const [charCount, setCharCount] = useState(0);
  const [validated, setValidated] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFeedbackChange = (e) => {
    const value = e.target.value;
    setData(prev => ({
      ...prev,
      problem: value
    }));
    setCharCount(value.length);
  };

  const handleSubmit = async(e) => {
    e.preventDefault();
    const form = e.currentTarget;
    
    if (!form.checkValidity()) {
      e.stopPropagation();
    } else {
      // Handle form submission
      const form_data = new FormData();
      form_data.append("phone",data.phone);
      form_data.append("file_id",data.file_id);
      form_data.append("problem",data.problem);
      const response = await axios.post(`${process.env.REACT_APP_SERVER_NAME}/sirpur-report`,data,{headers:{"Content-Type":"application/json"}});
      if(response.status === 200){
        toast.success("We got your report,\n we will resolve your problem",{duration:4444})
      }
      else{

      }
      setData({ phone: '', file_id: '', problem: '' });
      setCharCount(0);
      setValidated(false);
    }
    
    setValidated(true);
  };

  return (
    <div className="feedback-container">
            <div style={{justifyContent:'center', display:'flex'}}>
          <div className="feedback-box">
        <h3 className="text-center mb-4">Report Problem</h3>

        <form 
          className={`needs-validation ${validated ? 'was-validated' : ''}`}
          onSubmit={handleSubmit}
          noValidate
        >
          <div className="mb-3">
            <label className="form-label">Phone</label>
            <input
              type="tel"
              className="form-control"
              placeholder="Enter your 10-digit phone number"
              name="phone"
              value={data.phone}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, '').slice(0, 10);
                setData(prev => ({
                  ...prev,
                  phone: value
                }));
              }}
              maxLength="10"
              pattern="\d{10}"
              required
            />
            <div className="invalid-feedback">
              Please provide a valid 10-digit phone number.
            </div>
          </div>

          <div className="mb-3">
            <label className="form-label">File ID</label>
            <input
              type="text"
              className="form-control"
              placeholder="Enter file ID"
              name="file_id"
              value={data.file_id}
              onChange={handleInputChange}
              required
            />
            <div className="invalid-feedback">
              Please provide a file ID.
            </div>
          </div>

          <div className="mb-3">
            <label className="form-label">Problem</label>
            <textarea
              id="problem"
              className="form-control"
              rows="5"
              maxLength="100"
              placeholder="Describe the problem..."
              name="problem"
              value={data.problem}
              onChange={handleFeedbackChange}
              required
            ></textarea>
            <small className="text-muted">
              <span id="charCount">{charCount}</span>/100 characters
            </small>
            <div className="invalid-feedback">
              Please provide problem details.
            </div>
          </div>

          <div className="d-grid">
            <button type="submit" className="btn btn-primary">Submit</button>
          </div>
        </form>
      </div>
      </div>
      <Toaster position='top-center'/>
    </div>
  );
}
