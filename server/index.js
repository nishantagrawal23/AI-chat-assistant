import express from "express";
import multer from "multer";
import axios from "axios";
import cors from "cors";
import FormData from "form-data";

const app = express();
app.use(cors());
app.use(express.json());

const upload = multer({ storage: multer.memoryStorage() });

app.post("/upload", upload.single("file"), async (req, res) => {
    const formData = new FormData();
    formData.append("file", req.file.buffer, req.file.originalname);

    const response = await axios.post("http://127.0.0.1:8000/upload", formData, {
        headers: formData.getHeaders(),
    });

    res.json(response.data);
});

app.post("/query", async (req, res) => {
    const response = await axios.post("http://127.0.0.1:8000/query", {
        question: req.body.question,
    });

    res.json(response.data);
});

app.listen(5000, () => console.log("Server running on port 5000"));