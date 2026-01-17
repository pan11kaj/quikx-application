import react, { useEffect, useState } from "react";
import "../styles/queue.css";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import axios from "axios";
import useWebSocket, { ReadyState } from "react-use-websocket";
const statusMap = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Connected',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
};



export default function Queue() {
    const [queueList, setQueueList] = useState([]);
    const [searchParams] = useSearchParams();
    const [current_file_id, set_current_file_id] = useState(null)
    const { sendJsonMessage, lastMessage, readyState } = useWebSocket(`${process.env.REACT_APP_WEBSOCKET}/printers/queue-clients?printer_name=${searchParams.get("printer_name")}`);
    const navigate = useNavigate()

    useEffect(() => {
        if (lastMessage !== null) {
            try {
                const data = JSON.parse(lastMessage.data);
                console.log(data)
                if (data.success_file_id !== null) {
                    if (data.success_file_id.toString() === current_file_id) {
                        navigate(`/success?file_id=${current_file_id}&xxd=${searchParams.get("xxd")}&xxy=${searchParams.get("xxy")}`)
                    }
                }
                if (data.queue && Array.isArray(data.queue)) {
                    setQueueList(data.queue);
                }
            } catch (error) {
                console.error("Error parsing websocket data:", error);
            }
        }
    }, [lastMessage]);

    useEffect(() => {

        const fetchData = async () => {


            const printer_name = searchParams.get("printer_name")
            const url = process.env.REACT_APP_SERVER_NAME
            try {
                const response = await axios.post(url + "/printers/check-valid-printer", null, { params: { printer_name: printer_name } })
                if (response.status !== 404) {
                    const isValid = response.data.valid
                    set_current_file_id(searchParams.get("file_id"))
                    return isValid;
                }
            } catch (err) {
                return false
            }
        }
        fetchData().then((data) => {
            if (data === false) {
                navigate("/404")
            }
        })
    }, []);

    const matchFileId = (item) => current_file_id === item.file_id.toString()
    return (
        <div className="queue-container">
            <div className="queue-header" style={{width:"100vw"}}>
                <div className="header-background"></div>
                <h1 className="queue-title" style={{ textAlign: "center" }}>Printing Status</h1>
            </div>
            <div className="queue-list">
                {queueList.length > 0 ? (
                    queueList.map((item, index) => (
                        <div
                            key={item}
                            className="queue-item"
                            style={{ animationDelay: `${index * 0.05}s` }}
                        >
                            <div className="position-badge">
                                <span className="position-number">{index + 1}</span>
                            </div>

                            <div className="user-info">
                                {
                                    index === 0 ? <h3 className="user-name">Printing...</h3> :
                                        <h3 className="user-name">{matchFileId(item) ? "Your Task" : item.file_name}</h3>
                                }
                            </div>
                            <div className="status-indicator">
                                {
                                    index === 0 ?
                                        <div className="pulse-dot"></div>
                                        : matchFileId(item) ? <div className="pulse-left-arrow"></div> : <></>}
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="empty-queue">
                        <p>No items in queue</p>
                    </div>
                )}
            </div>

        </div>
    )
}