import React, { useEffect, useRef, useState } from "react";
import styles from "../styles/Home.module.css";
import pdfImage from "./pdfImage.png";
import docImage from "./docImage.png";
import imgImage from "./imgImage.png";
import FileViewModal from "./Modal";
import axios from "axios";
import toast, { Toaster } from "react-hot-toast";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
function Home() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [fileUrl, setFileUrl] = useState("");
  const [showFileContent, setShowFileContent] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [printer_name,set_printer_name] = useState(()=>searchParams.get("printer_name"))
  const [progressUpload, setProgressUpload] = useState(0);

  useEffect(() => {
const ids = localStorage.getItem("file_ids");

    if(ids === null){
           localStorage.setItem("file_ids",JSON.stringify([])) 
           
          }
    const fetchData = async () => {

      const url = process.env.REACT_APP_SERVER_NAME
      try {
        const response = await axios.post(url + "/printers/check-valid-printer", null, { params: { printer_name: printer_name } })
        if (response.status !== 404) {
          const isValid = response.data.valid
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
    });
            
  }, []);

  const uploadFile = async () => {
    const formData = new FormData();
    formData.append("file", file);
    const server_name = process.env.REACT_APP_SERVER_NAME;
    console.log(server_name)

    try {
      const response = await axios.post(server_name + "/printers/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }, params: { printer_name: printer_name }, onUploadProgress: (ProgressEvent) => {
          const percent = Math.round(ProgressEvent.loaded * 100) / ProgressEvent.total;
          setProgressUpload(percent);
          console.log(percent)
        }
      },);
      await start_payment(response.data.amount, response.data.id, printer_name, server_name, response.data.no_of_pages,response.data.file_name);
    } catch (error) {
      console.log(error);
    }


  }

  const loadRazorpay = () => {
    return new Promise((resolve) => {
      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  }

  const start_payment = async (amount, id, printer_name, server_name, no_of_pages,file_name) => {
    const res = await loadRazorpay();
    if (!res) {
      alert("Some error occured from your side!! please reload the site");
    }
    const orderResponse = await axios.post(server_name + `/printers/create-order/${amount}`, null, { params: { printer_name: printer_name } });
    console.log(id)

    const options = {
      key: process.env.REACT_APP_RAZORPAY_ID,
      amount: orderResponse.data.amount,
      currency: "INR",
      name: "Pay to QuikX",
      description: "charge for printouts",
      order_id: orderResponse.data.order_id,
      handler: async function (response) {
        try {
          const response2 = await axios.post(server_name + `/printers/verify/${id}/${amount}`, null, {
            params: {
              printer_name: printer_name,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature
            }
          });

          if (response2.data.event === "successful") {
            const ids = localStorage.getItem("file_ids");
          console.log(ids);
            const data = JSON.parse(ids);
            data.push(id);
            localStorage.setItem("file_ids",JSON.stringify(data));
            navigate(`/print-status?printer_name=${printer_name}&file_id=${id}&xxd=${no_of_pages}&xxy=${orderResponse.data.amount}`)
          }
        } catch (err) {
          console.error("Error in verifying payment:", err.response?.data || err.message);
        }
      },
      prefill: {
        name: "Pankaj Sahu",
        email: "pankaj@email.com",
        contact: "9999999999"
      },
      theme: {
        color: "#3399cc"
      },
      /// NOTE: failure or on fatal error must be implemented in the context
    };
    const paymentObject = new window.Razorpay(options);
    paymentObject.open();
  }

  const handleFileUpload = (e) => {
    console.log(file);

    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    
    // Create object URL for the file
    const url = URL.createObjectURL(selectedFile);
    setFileUrl(url);
    
    e.target.value = null;
  }

  const clickHandler = (type_of_file) => {
    console.log(file);

    inputRef.current.setAttribute("accept", type_of_file);
    inputRef.current.click();

  }

  return <>
    <div className={styles.container} style={{ userSelect: "none" }}>
      <div className={styles.heading}>

        <h1 >
          Welcome to
        </h1>

        <h1 className={styles.headingText}>
          Quik<b >X</b>
        </h1>

      </div>
      {
        file === null?

          <div className={styles.mainBody} >
            <h2 className={styles.choose_file_heading} >Choose a file to print</h2>
            <div style={{ display: 'flex', justifyContent: 'center', flexDirection: "column", alignItems: 'center', width: '100%', gap: '15px' }}>
              <div className={styles.mainBodyItemCard} onClick={() => clickHandler(".pdf")}><img src={pdfImage} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              </div>
              <div className={styles.mainBodyItemCard} onClick={() => clickHandler(".doc,.docx")}>
                <img src={docImage} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              </div>

              <div className={styles.mainBodyItemCard} onClick={() => clickHandler(".jpg,.png,.jpeg,.webp")}>
                <img src={imgImage} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              </div>


            </div>
            <button className={styles.choose_button} onClick={() => clickHandler("*")}>Choose Recent File</button>

          </div>
          :<>
          <div style={{ display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
            <h5 style={{color:"whitesmoke"}}>your file:</h5>
            <span className={styles.fileName} onClick={() => { 
              setShowFileContent(!showFileContent)
               }}>{file.name}</span>
            <div>
              <button className={styles.uploadingButtons} style={{ background: "linear-gradient(135deg, #059669, #10b981)" }} onClick={uploadFile}>Upload</button>
              <button className={styles.uploadingButtons} style={{ background: "linear-gradient(135deg, #dc2626, #ef4444)" }} onClick={() => { 
                setFile(null);
                setShowFileContent(false);
                if(fileUrl) URL.revokeObjectURL(fileUrl);
                setFileUrl("");
              }}>Cancel</button>
            </div>
          </div>
     <FileViewModal file={{name: file?.name, url: fileUrl}} setMode={setShowFileContent} dialogMode={showFileContent} />
</>
      }
      <input type="file" style={{ display: "none" }} ref={inputRef} onChange={handleFileUpload} />

    </div>
    <Toaster position="bottom-center" />
  </>
}


export default Home;


// //  <svg
//   
//   xmlns="http://www.w3.org/2000/svg"
//   viewBox="0 0 128 128"
// >
//   <defs>
//     <linearGradient id="bgGradientPdf" x1="0" y1="0" x2="1" y2="1">
//       <stop offset="0%" stopColor="#FB7185" />
//       <stop offset="100%" stopColor="#E11D48" />
//     </linearGradient>

//     <filter id="shadowPdf" x="-20%" y="-20%" width="140%" height="140%">
//       <feDropShadow
//         dx="6"
//         dy="8"
//         stdDeviation="10"
//         floodColor="#000"
//         floodOpacity="0.25"
//       />
{/* <Modal/> */ }
// Source - https://stackoverflow.com/a
// Posted by Jasperan, modified by community. See post 'Timeline' for change history
// Retrieved 2026-01-06, License - CC BY-SA 4.0
//     </filter>
//   </defs>

//   <rect
//     x="16"
//     y="16"
//     width="96"
//     height="96"
//     rx="28"
//     fill="url(#bgGradientPdf)"
//     filter="url(#shadowPdf)"
//   />

//   <rect
//     x="42"
//     y="34"
//     width="44"
//     height="60"
//     rx="6"
//     fill="white"
//   />

//   <path
//     d="M86 34v14H72Z"
//     fill="#F1F5F9"
//   />

//   <text
//     x="64"
//     y="74"
//     textAnchor="middle"
//     fill="#E11D48"
//     fontSize="16"
//     fontWeight="700"
//     fontFamily="Inter, Arial, Helvetica, sans-serif"
//   >
//     PDF
//   </text>
// </svg>	  