import react, { useEffect, useState } from "react";
import "../styles/queue.css";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";
import useWebSocket, { ReadyState } from "react-use-websocket";
const statusMap = {
  [ReadyState.CONNECTING]: 'Connecting',
  [ReadyState.OPEN]: 'Connected',
  [ReadyState.CLOSING]: 'Closing',
  [ReadyState.CLOSED]: 'Closed',
};



export default function Queue() {
    const [users] = useState([]);
    const [searchParams] = useSearchParams();
    const {sendJsonMessage,lastMessage,readyState} = useWebSocket(`ws://localhost:8000/printers/queue-clients?printer_name=${searchParams.get("printer_name")}`);
    const navigate = useNavigate()
    useEffect(() => {

        const fetchData = async()=>{

        
        const printer_name  = searchParams.get("printer_name")
        console.log(printer_name)
        const url = process.env.REACT_APP_SERVER_NAME
        try{
        const response = await axios.post(url+"/printers/check-valid-printer",null,{params:{printer_name:printer_name}})
        if( response.status !== 404){
            const isValid = response.data.valid
            console.log(isValid)
            return isValid;
        }
    }catch(err){
        return false
    }
}
fetchData().then((data)=>{
    if(data === false){
        navigate("/404")
    }
})
    }, []);
    

    return (
        <div className="queue-container">
            <div className="queue-header">
                <div className="header-background"></div>
                <h1 className="queue-title" style={{ textAlign: "center" }}>Printing Status</h1>

            </div>
            <h1>{statusMap[readyState]}</h1>
            <h1>{lastMessage?.data}</h1>
            <div className="queue-list">
                {users.map((user, index) => (
                    <div
                        key={user.id}
                        className="queue-item"
                        style={{ animationDelay: `${index * 0.05}s` }}
                    >
                        <div className="position-badge">
                            <span className="position-number">{user.position}</span>
                        </div>

                        <div className="user-info">
                            <h3 className="user-name">{user.name}</h3>
                        </div>
                        <div className="status-indicator">
                            <div className="pulse-dot"></div>
                        </div>
                    </div>
                ))}
            </div>
            
        </div>
    )
}