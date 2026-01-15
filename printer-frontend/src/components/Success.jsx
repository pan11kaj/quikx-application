import React from "react";
import { useSearchParams } from "react-router-dom";
import "../styles/success.css";

export default function Success() {
    const [searchParams] = useSearchParams();
    const fileId = searchParams.get("file_id");
    const amount = parseInt(searchParams.get("xxy"));
    const no_of_pages = parseInt(searchParams.get("xxd"));
    const date = new Date().toLocaleDateString();
    const time =new Date().toLocaleTimeString();

    return (
        <div className="success-container">
            <div className="success-card">
                <div className="success-icon">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                        <path d="M8 12l2.5 2.5L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                </div>
                <h1 className="success-title">Thank You!</h1>
                <p className="success-subtitle">Your print has been successfully printed!</p>
                
                <div className="success-details">
                    <div className="detail-item">
                        <span className="detail-label">File ID</span>
                        <span className="detail-value">{fileId}</span>
                    </div>
                    <div className="detail-divider"></div>
                    <div className="detail-item">
                        <span className="detail-label">No. of pages</span>
                        <span className="detail-value">{no_of_pages}</span>
                    </div>
                    <div className="detail-divider"></div>
                    <div className="detail-item">
                        <span className="detail-label">Amount</span>
                        <span className="detail-value">{amount/100} /-</span>
                    </div>
<div className="detail-item">
                        <span className="detail-label">Time</span>
                        <span className="detail-value">{time}</span>
                    </div>
                <div className="detail-item">
                        <span className="detail-label">Time</span>
                        <span className="detail-value">{date}</span>
                    </div>
                </div>

            </div>
        </div>
    );
}
