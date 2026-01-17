import react from "react";
import styles from "../styles/dialog.module.css";

const FileViewModal = ({file,setMode,dialogMode})=>{
	return (
		<div className={`${styles.mainContainer} ${dialogMode?styles.show:''}`} style={{display:`${dialogMode===false?'none':'block'}`}}>
			<div className={styles.modalContent}>
				<div className={styles.closeButton}>
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
				
				<div className={styles.fileContentContainer}>
					<h2 className={styles.fileName}>{file?.name || 'File Preview'}</h2>
					<div className={styles.fileContent}>
						{file?.url ? (
							<>
								{file.name?.endsWith('.pdf') ? (
									<iframe 
										src={file.url} 
										style={{ width: '100%', height: '100%', border: 'none', borderRadius: '6px' }}
										title="PDF preview"
									></iframe>
								) : file.name?.match(/\.(jpg|jpeg|png|gif|webp)$/i) ? (
									<img src={file.url} alt="File preview" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', display: 'block', margin: '0 auto' }} />
								) : file.name?.match(/\.(doc|docx)$/i) ? (
									<div style={{
										color: '#f1f1f1',
										fontFamily: '"Courier New", monospace',
										fontSize: '0.9rem',
										lineHeight: '1.6',
										whiteSpace: 'pre-wrap',
										wordBreak: 'break-word',
										padding: '10px'
									}}>
										<p>📄 Document file: {file.name}</p>
										<p style={{ fontSize: '0.85rem', color: '#7a7a7a' }}>Preview not available. Please upload to view.</p>
									</div>
								) : (
									<div style={{
										color: '#f1f1f1',
										fontFamily: '"Courier New", monospace',
										fontSize: '0.9rem',
										lineHeight: '1.6',
										whiteSpace: 'pre-wrap',
										wordBreak: 'break-word',
										padding: '10px'
									}}>
										<p>📁 File: {file.name}</p>
									</div>
								)}
							</>
						) : (
							<p>No file selected</p>
						)}
					</div>
				</div>
			</div>
		</div>
	)
}

export default FileViewModal;