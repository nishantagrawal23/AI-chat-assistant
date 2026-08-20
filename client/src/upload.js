import axios from "axios";

function Upload({ setIsUploaded }) {
    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append("file", file);
        try {
            setIsUploaded(false);
            await axios.post(`${import.meta.env.VITE_API_URL}/upload`, formData);
            alert("Resume uploaded!");
            setIsUploaded(true);
        } catch (err) {
            console.error(err);
            alert("Upload failed");
        }
    };
    return (
        <div className="upload">
            <input type="file" onChange={handleUpload} />
        </div>
    );
}

export default Upload;