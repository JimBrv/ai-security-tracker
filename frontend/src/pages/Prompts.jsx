import React, { useState, useEffect } from 'react';

const Prompts = () => {
    const [prompts, setPrompts] = useState([]);
    const [selectedPrompt, setSelectedPrompt] = useState(null);
    const [editTemplate, setEditTemplate] = useState("");
    const [message, setMessage] = useState(null);

    useEffect(() => {
        fetchPrompts();
    }, []);

    const fetchPrompts = async () => {
        try {
            const response = await fetch('http://localhost:8000/prompts');
            if (!response.ok) throw new Error("Failed to fetch prompts");
            const data = await response.json();
            setPrompts(data);
        } catch (error) {
            console.error("Error fetching prompts:", error);
            setMessage({ type: "error", text: "Failed to load prompts." });
        }
    };

    const handleSelectPrompt = (prompt) => {
        setSelectedPrompt(prompt);
        setEditTemplate(prompt.template);
        setMessage(null);
    };

    const handleSavePrompt = async () => {
        if (!selectedPrompt) return;

        try {
            const updatedPrompt = { ...selectedPrompt, template: editTemplate };
            const response = await fetch(`http://localhost:8000/prompts/${selectedPrompt.name}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedPrompt)
            });

            if (!response.ok) throw new Error("Failed to update prompt");

            setMessage({ type: "success", text: "Prompt updated successfully!" });
            fetchPrompts(); // Refresh list to confirm update
        } catch (error) {
            console.error("Error updating prompt:", error);
            setMessage({ type: "error", text: "Failed to update prompt." });
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8 text-gray-800 dark:text-gray-100">AI Prompt Management</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* List of Prompts */}
                <div className="md:col-span-1 bg-white dark:bg-gray-800 p-4 rounded-xl shadow-md border border-gray-100 dark:border-gray-700">
                    <h2 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200">Available Prompts</h2>
                    <ul className="space-y-2">
                        {prompts.map((p) => (
                            <li
                                key={p.name}
                                onClick={() => handleSelectPrompt(p)}
                                className={`p-3 rounded-lg cursor-pointer transition-colors ${selectedPrompt?.name === p.name
                                        ? "bg-blue-100 dark:bg-blue-900 border-l-4 border-blue-500"
                                        : "hover:bg-gray-50 dark:hover:bg-gray-700"
                                    }`}
                            >
                                <div className="font-medium text-gray-800 dark:text-gray-200">{p.name}</div>
                                <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{p.description}</div>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Editor */}
                <div className="md:col-span-2 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md border border-gray-100 dark:border-gray-700">
                    {selectedPrompt ? (
                        <>
                            <div className="flex justify-between items-center mb-6">
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{selectedPrompt.name}</h2>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{selectedPrompt.description}</p>
                                </div>
                                <button
                                    onClick={handleSavePrompt}
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors shadow-sm"
                                >
                                    Save Changes
                                </button>
                            </div>

                            {message && (
                                <div className={`mb-4 p-3 rounded-lg ${message.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                    {message.text}
                                </div>
                            )}

                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Template
                                </label>
                                <div className="relative">
                                    <textarea
                                        value={editTemplate}
                                        onChange={(e) => setEditTemplate(e.target.value)}
                                        className="w-full h-96 p-4 font-mono text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-800 dark:text-gray-200"
                                    />
                                    <div className="absolute top-2 right-2 text-xs text-gray-400">
                                        Input Variables: {selectedPrompt.input_variables.join(", ")}
                                    </div>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-gray-400">
                            <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <p>Select a prompt from the list to edit</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Prompts;
