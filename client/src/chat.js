import { useState } from "react";

function Chat({ isUploaded }) {
    const [q, setQ] = useState("");
    const [ans, setAns] = useState("");
    const [loading, setLoading] = useState(false);

    const ask = () => {
        setAns("");
        setLoading(true);

        const eventSource = new EventSource(
            `${import.meta.env.VITE_API_URL}/query-stream?question=${encodeURIComponent(q)}`
        );

        eventSource.onmessage = (event) => {
            setAns((prev) => prev + event.data);
        };

        eventSource.onerror = () => {
            eventSource.close();
            setLoading(false);
        };
    };

    return (
        <div className="container">
            <div className="input-container">
                <input
                    disabled={!isUploaded}
                    onChange={(e) => setQ(e.target.value)}
                    placeholder="Write your question here"
                />
                <button
                    disabled={!isUploaded}
                    onClick={ask}>
                    {loading ? "Thinking..." : "Ask"}
                </button>
            </div>
            <p className="answer">{ans}</p>
        </div>
    );
}

export default Chat;