import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Trash2, Globe, Play, Loader2, Clock, FileText } from 'lucide-react';

export default function Settings() {
    const [websites, setWebsites] = useState([]);
    const [loading, setLoading] = useState(true);
    const [scanningId, setScanningId] = useState(null);
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

    return (
        <div className="pt-24 pb-12 px-4 max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Data Sources</h1>
                    <p className="text-slate-400">Manage the intelligence feeds monitored by the agents.</p>
                </div>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors font-medium"
                >
                    <Plus className="w-4 h-4" />
                    Add Source
                </button>
            </div>

            {isAdding && (
                <div className="mb-8 glass-panel p-6 rounded-xl border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4">Add New Source</h3>
                    <form onSubmit={handleAddSite} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm text-slate-400 mb-1">Name</label>
                                <input
                                    required
                                    type="text"
                                    value={newSite.name}
                                    onChange={e => setNewSite({ ...newSite, name: e.target.value })}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-slate-400 mb-1">URL</label>
                                <input
                                    required
                                    type="url"
                                    value={newSite.url}
                                    onChange={e => setNewSite({ ...newSite, url: e.target.value })}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Description</label>
                            <input
                                type="text"
                                value={newSite.description}
                                onChange={e => setNewSite({ ...newSite, description: e.target.value })}
                                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
                            />
                        </div>
                        <div className="flex justify-end gap-3">
                            <button
                                type="button"
                                onClick={() => setIsAdding(false)}
                                className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
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
                    <div key={site.id} className="glass-card p-4 rounded-xl flex items-center justify-between group hover:border-slate-600 transition-all">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-slate-800 rounded-lg text-slate-400 group-hover:text-blue-400 transition-colors">
                                <Globe className="w-5 h-5" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-200">{site.name}</h3>
                                <a href={site.url} target="_blank" rel="noreferrer" className="text-xs text-blue-400 hover:underline mb-1 block">{site.url}</a>
                                <p className="text-sm text-slate-500 mb-2">{site.description}</p>
                                <div className="flex items-center gap-4 text-xs text-slate-500">
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
                                disabled={scanningId === site.id}
                                className="p-2 text-slate-400 hover:text-green-400 hover:bg-green-500/10 rounded-lg transition-colors disabled:opacity-50"
                                title="Run Agent Scan"
                            >
                                {scanningId === site.id ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
                            </button>
                            <button
                                onClick={() => handleDelete(site.id)}
                                className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
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
