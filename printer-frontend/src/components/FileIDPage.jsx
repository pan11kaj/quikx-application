import react, { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import '../styles/fileid.css';

export const FileIDPage = ()=>{
    const navigate = useNavigate();
    const [file_ids,set_file_ids] = useState(()=>{
        const ids = localStorage.getItem("file_ids");
        if(ids === null){
            return null
        }
        const data = JSON.parse(ids);
        
        return data;
    })

    // Sort file_ids in descending order
    const sortedFileIds = file_ids ? [...file_ids].sort((a, b) => b - a) : [];

    return file_ids === null?navigate("/404"):(
        <div className="fileid-container">
            <div className="fileid-wrapper">
                <h1 className="fileid-title">File IDs</h1>
                
                {sortedFileIds.length === 0 ? (
                    <div className="empty-state">
                        <p>No file IDs available</p>
                    </div>
                ) : (
                    <div className="fileid-grid">
                        {sortedFileIds.map((id, index) => (
                            <div key={index} className="fileid-card">
                                <div className="fileid-number">{id}</div>
                                {/* <div className="fileid-index">#{index + 1}</div> */}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}