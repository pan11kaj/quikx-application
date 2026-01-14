import react from "react";
import styles from "../styles/dialog.module.css";

const FileViewModal = ({file,setMode,dialogMode})=>{
	return (
		<div className={`${styles.mainContainer} ${dialogMode?styles.show:''}`} style={{display:`${dialogMode===false?'none':'block'}`}}>
				s
				<div className={"closeButton"}>
					
    <svg
      width={50}
      height={50}
      viewBox="0 0 24 24"
	  onClick={()=>setMode(false)}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <line x1="5" y1="5" x2="19" y2="19" stroke="currentColor" strokeWidth="2" />
      <line x1="19" y1="5" x2="5" y2="19" stroke="currentColor" strokeWidth="2" />
    </svg>
  


				</div>
		</div>
	)
}

export default FileViewModal;