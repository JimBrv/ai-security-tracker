import React from 'react';
import { Cpu, ScanEye, Network, LayoutDashboard, Settings as SettingsIcon, Sun, Moon, MessageSquare } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, darkMode, toggleDarkMode }) {
    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 h-16 border-b transition-colors ${darkMode ? 'glass-panel border-slate-800' : 'bg-white/80 backdrop-blur-xl border-slate-200 shadow-sm'}`}>
            <div className="max-w-7xl mx-auto px-4 h-full flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className={`relative p-2 rounded-xl border transition-all duration-300 ${darkMode
                        ? 'bg-gradient-to-br from-cyan-600/20 to-emerald-600/20 border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.3)]'
                        : 'bg-gradient-to-br from-cyan-50 to-emerald-50 border-cyan-100 shadow-cyan-100'
                        }`}>
                        <Cpu className={`w-8 h-8 ${darkMode ? 'text-cyan-400' : 'text-cyan-600'}`} />
                        <div className="absolute inset-0 flex items-center justify-center">
                            <ScanEye className={`w-4 h-4 ${darkMode ? 'text-emerald-300' : 'text-emerald-500'}`} />
                        </div>
                    </div>
                    <span className={`text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r ${darkMode
                        ? 'from-cyan-400 via-teal-400 to-emerald-400'
                        : 'from-cyan-600 via-teal-600 to-emerald-600'
                        }`}>
                        AI Security Tracker
                    </span>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setActiveTab('dashboard')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${activeTab === 'dashboard'
                            ? (darkMode ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-blue-50 text-blue-600 border border-blue-100')
                            : (darkMode ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100')
                            }`}
                    >
                        <LayoutDashboard className="w-4 h-4" />
                        <span>Dashboard</span>
                    </button>

                    <button
                        onClick={() => setActiveTab('settings')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${activeTab === 'settings'
                            ? (darkMode ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-blue-50 text-blue-600 border border-blue-100')
                            : (darkMode ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100')
                            }`}
                    >
                        <SettingsIcon className="w-4 h-4" />
                        <span>Sources</span>
                    </button>

                    <button
                        onClick={() => setActiveTab('prompts')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${activeTab === 'prompts'
                            ? (darkMode ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-blue-50 text-blue-600 border border-blue-100')
                            : (darkMode ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100')
                            }`}
                    >
                        <MessageSquare className="w-4 h-4" />
                        <span>Prompts</span>
                    </button>

                    <div className={`w-px h-6 mx-2 ${darkMode ? 'bg-slate-800' : 'bg-slate-200'}`} />

                    <button
                        onClick={toggleDarkMode}
                        className={`p-2 rounded-lg transition-all ${darkMode
                            ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                            }`}
                        title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
                    >
                        {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                    </button>
                </div>
            </div>
        </nav>
    );
}
