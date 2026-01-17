import React, { useState } from 'react';
import '../styles/feedback.css';
import axios from 'axios';

export default function Feedback() {
  const [data, setData] = useState({
    name: '',
    email: '',
    feedback: '',
    suggestions: ''
  });
  const [charCount, setCharCount] = useState(0);
  const [suggestionsCount, setSuggestionsCount] = useState(0);
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
      feedback: value
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
      form_data.append("name",data.name);
      form_data.append("email",data.email);
      form_data.append("feedback",data.feedback);
      form_data.append("suggestions",data.suggestions);
      const response = await axios.post(`${process.env.REACT_APP_SERVER_NAME}/sirpur-review`,data,{headers:{"Content-Type":"application/json"}});
      if(response.status === 200){
            console.log("HELLO WORL")
      }
      else{

      }
      setData({ name: '', email: '', feedback: '', suggestions: '' });
      setCharCount(0);
      setSuggestionsCount(0);
      setValidated(false);
    }
    
    setValidated(true);
  };

  return (
    <div className="feedback-container">
            <div style={{justifyContent:'center', display:'flex'}}>
          <div className="feedback-box">
        <h3 className="text-center mb-4">Feedback Form</h3>

        <form 
          className={`needs-validation ${validated ? 'was-validated' : ''}`}
          onSubmit={handleSubmit}
          noValidate
        >
          <div className="mb-3">
            <label className="form-label">Name</label>
            <input
              type="text"
              className="form-control"
              placeholder="Enter your name"
              name="name"
              value={data.name}
              onChange={handleInputChange}
              required
            />
            <div className="invalid-feedback">
              Please provide your name.
            </div>
          </div>

          <div className="mb-3">
            <label className="form-label">Email address</label>
            <input
              type="email"
              className="form-control"
              placeholder="Enter your email"
              name="email"
              value={data.email}
              onChange={handleInputChange}
              required
            />
            <div className="form-text">We'll never share your email.</div>
            <div className="invalid-feedback">
              Please provide a valid email address.
            </div>
          </div>

          <div className="mb-3">
            <label className="form-label">Your Feedback/Experience</label>
            <textarea
              id="feedback"
              className="form-control"
              rows="2"
              maxLength="100"
              placeholder="Write your feedback here..."
              name="feedback"
              value={data.feedback}
              onChange={handleFeedbackChange}
              required
            ></textarea>
            <small className="text-muted">
              <span id="charCount">{charCount}</span>/100 characters
            </small>
            <div className="invalid-feedback">
              Please provide your feedback.
            </div>
          </div>

          <div className="mb-3">
            <label className="form-label">Suggestions (Optional)</label>
            <textarea
              id="suggestions"
              className="form-control"
              rows="2"
              placeholder="Share any suggestions for improvement..."
              name="suggestions"
              value={data.suggestions}
              onChange={(e) => {
                const value = e.target.value;
                setData(prev => ({
                  ...prev,
                  suggestions: value
                }));
                setSuggestionsCount(value.length);
              }}
            ></textarea>
            
          </div>

          <div className="d-grid">
            <button type="submit" className="btn btn-primary">Submit</button>
          </div>
        </form>
      </div>
      </div>
    </div>
  );
}
