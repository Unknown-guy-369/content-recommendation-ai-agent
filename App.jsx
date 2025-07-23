import React, { useState } from "react";

const App = () => {
  const [response, setResponse] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResponse("");
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:5000/agent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: message }),
      });

      const data = await res.json();
      setResponse(data.response);
    } catch (e) {
      setResponse("Can't produce output");
      console.error("Error:", e);
    }
    setLoading(false);
  };

  return (
    <div className="bg-gray-900 min-h-screen flex justify-center items-center">
      <div className="bg-white w-[500px] max-h-[600px] rounded-2xl shadow-lg p-5 flex flex-col justify-between">
        <div className="overflow-auto mb-5 max-h-[400px] whitespace-pre-wrap text-gray-800">
          {loading ? <p className="text-blue-500"> Generating...</p> : <p>{response}</p>}
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2 items-center">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="flex-1 rounded-2xl border border-gray-400 px-4 py-2 focus:outline-none"
            type="text"
            placeholder="Enter your query"
            required
          />
          <button
            type="submit"
            className={`px-4 py-2 rounded-2xl text-white ${
              loading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
            }`}
            disabled={loading}
          >
            Submit
          </button>
        </form>
      </div>
    </div>
  );
};

export default App;
