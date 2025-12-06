import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Trash2, Globe, Play, Loader2, Clock, FileText } from 'lucide-react';

export default function Settings({ darkMode }) {
    const [websites, setWebsites] = useState([]);
    const [loading, setLoading] = useState(true);
    const [scanningId, setScanningId] = useState(null);
    const [batchScanning, setBatchScanning] = useState(false);
    const [scanProgress, setScanProgress] = useState({ current: 0, total: 0 });
    const [newSite, setNewSite] = useState({ name: '', url: '', description: '' });
    const [isAdding, setIsAdding] = useState(false);

    const fetchWebsites = async () => {
        try {
            const response = await axios.get('http://localhost:8000/websites');
            setWebsites(response.data);
        } catch (error) {
            console.error("Failed to fetch websites", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchWebsites();
    }, []);

    const handleAddSite = async (e) => {
        e.preventDefault();
        try {
            await axios.post('http://localhost:8000/websites', newSite);
            setNewSite({ name: '', url: '', description: '' });
            setIsAdding(false);
            fetchWebsites();
        } catch (error) {
            console.error("Failed to add website", error);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this source?')) return;
        try {
            await axios.delete(`http://localhost:8000/websites/${id}`);
            fetchWebsites();
        } catch (error) {
            console.error("Failed to delete website", error);
        }
    };

    const handleScan = async (id) => {
        setScanningId(id);
        try {
            await axios.post(`http://localhost:8000/scan/${id}`);
            alert('Scan started in background!');
        } catch (error) {
            console.error("Failed to start scan", error);
            alert('Failed to start scan');
        } finally {
            setScanningId(null);
        }
    };

    const handleBatchScan = async () => {
        if (!window.confirm(`Start scanning all ${websites.length} sources? This may take a while.`)) return;

        setBatchScanning(true);
        setScanProgress({ current: 0, total: websites.length });

        for (let i = 0; i < websites.length; i++) {
            const site = websites[i];
            setScanProgress({ current: i + 1, total: websites.length });

            try {
                await axios.post(`http://localhost:8000/scan/${site.id}`);
                console.log(`Scan started for: ${site.name}`);
            } catch (error) {
                console.error(`Failed to scan ${site.name}:`, error);
            }

            // Small delay between scans to avoid overwhelming the server
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        setBatchScanning(false);
        setScanProgress({ current: 0, total: 0 });
        alert(`Batch scan initiated for all ${websites.length} sources!`);
    };

    return (
        <div className="pt-24 pb-12 px-4 max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className={`text-3xl font-bold mb-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>Data Sources</h1>
                    <p className={darkMode ? 'text-slate-400' : 'text-slate-600'}>Manage the intelligence feeds monitored by the agents.</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleBatchScan}
                        disabled={batchScanning || websites.length === 0}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Scan all sources"
                    >
                        {batchScanning ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Scanning ({scanProgress.current}/{scanProgress.total})
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4" />
                                Scan All
                            </>
                        )}
                    </button>
                    <button
                        onClick={() => setIsAdding(!isAdding)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors font-medium"
                    >
                        <Plus className="w-4 h-4" />
                        Add Source
                    </button>
                </div>
            </div>

            {isAdding && (
                <div className={`mb-8 glass-panel p-6 rounded-xl border ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
                    <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>Add New Source</h3>
                    <form onSubmit={handleAddSite} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className={`block text-sm mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Name</label>
                                <input
                                    required
                                    type="text"
                                    value={newSite.name}
                                    onChange={e => setNewSite({ ...newSite, name: e.target.value })}
                                    className={`w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${darkMode
                                        ? 'bg-slate-950 border-slate-800 text-white'
                                        : 'bg-white border-slate-300 text-slate-900'
                                        }`}
                                />
                            </div>
                            <div>
                                <label className={`block text-sm mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>URL</label>
                                <input
                                    required
                                    type="url"
                                    value={newSite.url}
                                    onChange={e => setNewSite({ ...newSite, url: e.target.value })}
                                    className={`w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${darkMode
                                        ? 'bg-slate-950 border-slate-800 text-white'
                                        : 'bg-white border-slate-300 text-slate-900'
                                        }`}
                                />
                            </div>
                        </div>
                        <div>
                            <label className={`block text-sm mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Description</label>
                            <input
                                type="text"
                                value={newSite.description}
                                onChange={e => setNewSite({ ...newSite, description: e.target.value })}
                                className={`w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${darkMode
                                    ? 'bg-slate-950 border-slate-800 text-white'
                                    : 'bg-white border-slate-300 text-slate-900'
                                    }`}
                            />
                        </div>
                        <div className="flex justify-end gap-3">
                            <button
                                type="button"
                                onClick={() => setIsAdding(false)}
                                className={`px-4 py-2 transition-colors ${darkMode
                                    ? 'text-slate-400 hover:text-white'
                                    : 'text-slate-600 hover:text-slate-900'
                                    }`}
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
                            >
                                Save Source
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="space-y-4">
                {websites.map(site => (
                    <div key={site.id} className={`glass-card p-4 rounded-xl flex items-center justify-between group transition-all ${darkMode ? 'hover:border-slate-600' : 'hover:border-slate-300'
                        }`}>
                        <div className="flex items-start gap-4">
                            <div className={`p-3 rounded-lg transition-colors ${darkMode
                                ? 'bg-slate-800 text-slate-400 group-hover:text-blue-400'
                                : 'bg-slate-100 text-slate-500 group-hover:text-blue-600'
                                }`}>
                                <Globe className="w-5 h-5" />
                            </div>
                            <div>
                                <h3 className={`font-semibold ${darkMode ? 'text-slate-200' : 'text-slate-900'}`}>{site.name}</h3>
                                <a href={site.url} target="_blank" rel="noreferrer" className={`text-xs hover:underline mb-1 block ${darkMode ? 'text-blue-400' : 'text-blue-600'
                                    }`}>{site.url}</a>
                                <p className={`text-sm mb-2 ${darkMode ? 'text-slate-500' : 'text-slate-600'}`}>{site.description}</p>
                                <div className={`flex items-center gap-4 text-xs ${darkMode ? 'text-slate-500' : 'text-slate-600'}`}>
                                    <div className="flex items-center gap-1" title="Last Scanned">
                                        <Clock className="w-3 h-3" />
                                        <span>
                                            {site.last_scraped_at
                                                ? new Date(site.last_scraped_at).toLocaleString()
                                                : 'Never scanned'}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-1" title="Events Found">
                                        <FileText className="w-3 h-3" />
                                        <span>{site.event_count || 0} events</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => handleScan(site.id)}
                                disabled={scanningId === site.id || batchScanning}
                                className={`p-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${darkMode
                                        ? 'text-slate-400 hover:text-green-400 hover:bg-green-500/10'
                                        : 'text-slate-500 hover:text-green-600 hover:bg-green-50'
                                    }`}
                                title="Run Agent Scan"
                            >
                                {scanningId === site.id ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
                            </button>
                            <button
                                onClick={() => handleDelete(site.id)}
                                className={`p-2 rounded-lg transition-colors ${darkMode
                                    ? 'text-slate-400 hover:text-red-400 hover:bg-red-500/10'
                                    : 'text-slate-500 hover:text-red-600 hover:bg-red-50'
                                    }`}
                                title="Delete Source"
                            >
                                <Trash2 className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
