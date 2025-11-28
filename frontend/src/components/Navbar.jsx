import React from 'react';
import { Shield, LayoutDashboard, Settings as SettingsIcon } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
    return (
        <nav className="fixed top-0 left-0 right-0 z-50 glass-panel border-b border-slate-800 h-16">
            <div className="max-w-7xl mx-auto px-4 h-full flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                        <Shield className="w-6 h-6 text-blue-400" />
                    </div>
                    <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                        AI Security Tracker
                    </span>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setActiveTab('dashboard')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${activeTab === 'dashboard'
                                ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                            }`}
                    >
                        <LayoutDashboard className="w-4 h-4" />
                        <span>Dashboard</span>
                    </button>

                    <button
                        onClick={() => setActiveTab('settings')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${activeTab === 'settings'
                                ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                            }`}
                    >
                        <SettingsIcon className="w-4 h-4" />
                        <span>Sources</span>
                    </button>
                </div>
            </div>
        </nav>
    );
}
