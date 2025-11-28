import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';

function App() {
    const [activeTab, setActiveTab] = useState('dashboard');

    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-blue-500/30">
            <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

            <main>
                {activeTab === 'dashboard' && <Dashboard />}
                {activeTab === 'settings' && <Settings />}
            </main>
        </div>
    );
}

export default App;
