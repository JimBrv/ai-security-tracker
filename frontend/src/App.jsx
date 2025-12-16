import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';

import Prompts from './pages/Prompts';

function App() {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [darkMode, setDarkMode] = useState(false);

    const toggleDarkMode = () => {
        setDarkMode(!darkMode);
    };

    return (
        <div className={`min-h-screen font-sans selection:bg-blue-500/30 ${darkMode ? 'dark bg-slate-950 text-slate-50' : 'bg-slate-50 text-slate-900'}`}>
            <Navbar activeTab={activeTab} setActiveTab={setActiveTab} darkMode={darkMode} toggleDarkMode={toggleDarkMode} />

            <main>
                {activeTab === 'dashboard' && <Dashboard darkMode={darkMode} />}
                {activeTab === 'settings' && <Settings darkMode={darkMode} />}
                {activeTab === 'prompts' && <Prompts darkMode={darkMode} />}
            </main>
        </div>
    );
}

export default App;
